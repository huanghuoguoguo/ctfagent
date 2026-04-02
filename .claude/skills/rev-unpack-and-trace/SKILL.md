---
name: rev-unpack-and-trace
description: Triage CTF reverse engineering challenges. Use when a binary or executable must be understood to recover a flag, key, password, or hidden logic — no network service involved. Covers file identification, packer detection, static analysis, and guided dynamic analysis.
---

# Rev Unpack and Trace

Use this skill after `ctf-solver-profile` when evidence points to a reverse engineering challenge.

Treat it as a short SOP:

- identify the binary type and architecture
- detect packing or obfuscation before wasting time on garbage disassembly
- extract strings and symbols for quick wins
- apply static then dynamic analysis in increasing cost order

## Quick Start

Run the triage script:

```bash
python3 .claude/skills/rev-unpack-and-trace/scripts/rev_check.py ./challenge_binary
```

Save JSON output for later reference:

```bash
python3 .claude/skills/rev-unpack-and-trace/scripts/rev_check.py ./challenge_binary --output recon.json
```

## When to Use

- Challenge provides a binary and asks for a flag, key, password, or hidden logic.
- No network service to exploit (that distinguishes rev from pwn).
- Binary could be ELF, PE, Mach-O, .NET, Java JAR, or Python .pyc.

## When NOT to Use

Switch away when:

- Binary exposes a network service you must exploit. Use `pwn-initial-recon`.
- Challenge is about crypto math with no real binary RE. Use a crypto skill.
- Challenge is forensics, steganography, or memory dumps. Those are not RE triage.

## Probe Order

### Phase 1 — Identify

1. `file` command — architecture, type (ELF, PE, Mach-O, .NET, Java JAR, Python .pyc).
2. `strings` — flag format hints, URLs, passwords, crypto constants, debug messages.
3. Check for known packers:
   - UPX magic bytes (`UPX!`)
   - PyInstaller marker (`_MEIPASS`)
   - .NET headers (`MZ` + metadata tables)
   - Java JAR (`PK` header + `META-INF/MANIFEST.MF`)

### Phase 2 — Unpack if Needed

1. **UPX**: `upx -d binary` (overwrites in place; copy first).
2. **PyInstaller**: `pyinstxtractor` to extract, then `uncompyle6` or `decompyle3` on `.pyc`.
3. **.NET**: `ilspycmd` or `dnSpy` to decompile IL to C#.
4. **Java JAR**: `jar xf` to extract, then `cfr` or `procyon` to decompile `.class` files.
5. **Custom packer**: check per-section entropy. High entropy (> 7.0 on 0-8 scale) means packed or encrypted data.

If unpacking fails, note it as "needs manual RE" and keep going with raw strings and dynamic analysis.

### Phase 3 — Static Analysis

1. Disassemble entry point and main with `objdump -d` or Ghidra headless.
2. Identify key functions: `main`, `check_flag`, `validate`, `encrypt`, `decode`.
3. Trace data flow: where is user input read? Where is it compared?
4. Look for comparison patterns:
   - XOR loops with a fixed key
   - Table lookups or substitution boxes
   - Known crypto constants (AES S-box `0x63`, SHA-256 init `0x6a09e667`)

### Phase 4 — Dynamic Analysis (if Static Insufficient)

1. `ltrace` / `strace` — trace library calls and syscalls.
2. `gdb` with breakpoints on comparison functions (`strcmp`, `memcmp`, `strncmp`).
3. Watch memory at the comparison point to extract the expected value.
4. If anti-debug is detected (ptrace self-check, timing checks), patch or bypass:
   - `set *(int*)addr = 0x90909090` in gdb
   - `LD_PRELOAD` a fake `ptrace` that returns 0

## Common RE Patterns

| Pattern | Approach |
|---------|----------|
| XOR with fixed key | Extract key from binary, XOR ciphertext back |
| Custom encoding (base64 variant, ROT) | Reverse the transform step by step |
| `strcmp`/`memcmp` against hardcoded value | Read expected value from memory at runtime |
| Multi-stage: decode then decrypt then validate | Reverse each stage from the end backward |
| Constraint system (many conditions on input) | Feed to Z3 or angr for automated solving |
| VM-based obfuscation (custom bytecode) | Map opcodes, write a disassembler, then solve |

## Exit Conditions

Switch away from this skill when:

- Binary is a network service. Redirect to `pwn-initial-recon`.
- Binary is just a wrapper around crypto math. Redirect to a crypto skill.
- Packed with a custom protector and no quick unpack exists. Note as "needs manual RE" and escalate.
- Strings or quick dynamic analysis already reveal the flag. Capture with `ctf-knowledge-capture`.

## Tools

- `file`, `strings`, `objdump`, `readelf` — standard binutils
- `upx` — UPX unpacker
- `ltrace`, `strace` — dynamic tracing
- `gdb` — debugger with breakpoints and memory inspection
- `pyinstxtractor`, `uncompyle6`, `decompyle3` — Python reversing
- `cfr`, `procyon` — Java decompilers
- `ilspycmd` — .NET decompiler
- `angr`, `z3` — constraint solving (optional, for complex checks)
