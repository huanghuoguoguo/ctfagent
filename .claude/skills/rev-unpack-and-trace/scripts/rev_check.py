#!/usr/bin/env python3
"""
Rev Binary Triage — Identify, Unpack, and Trace

Quick triage for CTF reverse engineering challenges.  Identifies binary
type, detects common packers, computes section entropy, extracts
interesting strings, and checks for symbols.

Usage:
    python3 rev_check.py ./binary
    python3 rev_check.py ./binary --output recon.json
"""

import argparse
import json
import math
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Dict, List, Optional


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class RevResult:
    file_info: str
    architecture: str
    packer_detected: Optional[str]
    entropy_suspect: bool
    interesting_strings: List[str]
    symbols_present: bool
    recommended_next: List[str]
    sections: List[Dict[str, object]] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _run(cmd: List[str], timeout: int = 10) -> Optional[str]:
    """Run an external command and return stdout, or None on failure."""
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return proc.stdout
    except FileNotFoundError:
        return None
    except subprocess.TimeoutExpired:
        return None
    except Exception:
        return None


def _run_bytes(cmd: List[str], timeout: int = 10) -> Optional[bytes]:
    """Run an external command and return raw stdout bytes."""
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            timeout=timeout,
        )
        return proc.stdout
    except FileNotFoundError:
        return None
    except subprocess.TimeoutExpired:
        return None
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Phase 1 — Identify
# ---------------------------------------------------------------------------

def identify_file(path: str) -> str:
    """Return the output of `file` on the target."""
    out = _run(["file", "-b", path])
    if out:
        return out.strip()
    return "unknown (file command unavailable)"


def parse_architecture(file_info: str) -> str:
    """Extract a short architecture tag from the file output."""
    if "x86-64" in file_info or "x86_64" in file_info:
        return "x86-64"
    if "Intel 80386" in file_info or "i386" in file_info:
        return "i386"
    if "aarch64" in file_info or "ARM aarch64" in file_info:
        return "aarch64"
    if "ARM" in file_info:
        return "arm"
    if "MIPS" in file_info:
        return "mips"
    if "PE32+" in file_info:
        return "PE64"
    if "PE32" in file_info:
        return "PE32"
    if "Mach-O" in file_info:
        return "Mach-O"
    if ".Net" in file_info or "Mono" in file_info or "MSIL" in file_info:
        return ".NET-IL"
    if "Java" in file_info or "Zip archive" in file_info:
        return "Java/JAR"
    if "python" in file_info.lower() or "byte-compiled" in file_info.lower():
        return "Python-bytecode"
    return "unknown"


# ---------------------------------------------------------------------------
# Packer detection
# ---------------------------------------------------------------------------

PACKER_SIGNATURES: List[tuple] = [
    (b"UPX!", "UPX"),
    (b"_MEIPASS", "PyInstaller"),
    (b"PYZ-00", "PyInstaller"),
    (b"META-INF/MANIFEST.MF", "Java-JAR"),
]


def detect_packer(data: bytes) -> Optional[str]:
    """Scan first 64 KiB + last 16 KiB for known packer signatures."""
    size = len(data)
    head = data[:65536]
    if size > 65536:
        tail = data[-16384:]
    else:
        tail = b""
    blob = head + tail

    for sig, name in PACKER_SIGNATURES:
        if sig in blob:
            return name

    # .NET check: MZ header + "mscoree.dll" import hint
    if blob[:2] == b"MZ" and b"mscoree.dll" in blob:
        return ".NET-packed"

    return None


# ---------------------------------------------------------------------------
# Entropy
# ---------------------------------------------------------------------------

def _entropy(data: bytes) -> float:
    """Shannon entropy of a byte sequence (0.0 – 8.0 scale)."""
    if not data:
        return 0.0
    freq = [0] * 256
    for b in data:
        freq[b] += 1
    length = len(data)
    ent = 0.0
    for count in freq:
        if count == 0:
            continue
        p = count / length
        ent -= p * math.log2(p)
    return ent


def section_entropies(path: str, data: bytes) -> List[Dict[str, object]]:
    """Compute entropy per ELF section using readelf + raw reads."""
    out = _run(["readelf", "-S", "--wide", path])
    if not out:
        # Fallback: compute whole-file entropy
        return [{"name": "<whole-file>", "entropy": round(_entropy(data), 2),
                 "size": len(data)}]

    sections = []
    # Parse readelf section table lines
    for line in out.splitlines():
        m = re.search(
            r'\[\s*\d+\]\s+(\S+)\s+\S+\s+([0-9a-fA-F]+)\s+([0-9a-fA-F]+)\s+([0-9a-fA-F]+)',
            line,
        )
        if not m:
            continue
        name = m.group(1)
        offset = int(m.group(3), 16)
        size = int(m.group(4), 16)
        if size == 0:
            continue
        sections.append((name, offset, size))

    results = []
    for name, offset, size in sections:
        section_data = data[offset:offset + size]
        ent = round(_entropy(section_data), 2)
        results.append({"name": name, "entropy": ent, "size": size})

    return results


def has_entropy_suspect(sections: List[Dict[str, object]]) -> bool:
    """Return True if any code/data section has suspiciously high entropy."""
    for sec in sections:
        name = sec.get("name", "")
        ent = sec.get("entropy", 0.0)
        # Skip debug and string-table sections
        if name.startswith(".debug") or name in (".strtab", ".shstrtab", ".dynstr"):
            continue
        if ent >= 7.0:
            return True
    return False


# ---------------------------------------------------------------------------
# Strings
# ---------------------------------------------------------------------------

INTERESTING_PATTERNS = [
    re.compile(rb"flag\{[^}]{0,120}\}", re.IGNORECASE),
    re.compile(rb"CTF\{[^}]{0,120}\}", re.IGNORECASE),
    re.compile(rb"picoCTF\{[^}]{0,120}\}", re.IGNORECASE),
    re.compile(rb"password", re.IGNORECASE),
    re.compile(rb"secret", re.IGNORECASE),
    re.compile(rb"key[=: ]", re.IGNORECASE),
    re.compile(rb"https?://\S{4,80}"),
    re.compile(rb"correct|success|congrat", re.IGNORECASE),
    re.compile(rb"wrong|incorrect|denied|fail", re.IGNORECASE),
    re.compile(rb"/bin/sh|/bin/bash"),
]


def extract_interesting_strings(data: bytes, limit: int = 20) -> List[str]:
    """Pull interesting strings from the binary via regex over raw bytes."""
    found: List[str] = []
    for pat in INTERESTING_PATTERNS:
        for match in pat.finditer(data):
            text = match.group(0).decode("utf-8", errors="replace")
            if text not in found:
                found.append(text)
            if len(found) >= limit:
                return found

    return found


# ---------------------------------------------------------------------------
# Symbols
# ---------------------------------------------------------------------------

def check_symbols(path: str) -> bool:
    """Return True if the binary has a usable symbol table."""
    out = _run(["nm", "-C", path])
    if out and len(out.strip().splitlines()) > 2:
        return True
    # Try readelf for dynamic symbols
    out = _run(["readelf", "--dyn-syms", path])
    if out and "FUNC" in out:
        return True
    return False


# ---------------------------------------------------------------------------
# Recommendations
# ---------------------------------------------------------------------------

def recommend_next(
    file_info: str,
    arch: str,
    packer: Optional[str],
    entropy_suspect: bool,
    symbols: bool,
    interesting: List[str],
) -> List[str]:
    """Produce a short ordered list of recommended next steps."""
    steps: List[str] = []

    # Quick-win check
    for s in interesting:
        if re.search(r"flag\{", s, re.IGNORECASE) or re.search(r"CTF\{", s, re.IGNORECASE):
            steps.append("Possible flag literal found in strings — verify before deeper RE.")
            break

    # Unpack
    if packer == "UPX":
        steps.append("Unpack with: upx -d <binary> (copy original first).")
    elif packer == "PyInstaller":
        steps.append("Extract with pyinstxtractor, then decompile .pyc with uncompyle6/decompyle3.")
    elif packer == ".NET-packed":
        steps.append("Decompile with ilspycmd or dnSpy.")
    elif packer == "Java-JAR":
        steps.append("Extract with jar xf, decompile .class files with cfr or procyon.")
    elif packer:
        steps.append(f"Detected packer: {packer}. Attempt unpack before static analysis.")

    if entropy_suspect and not packer:
        steps.append("High section entropy without known packer — possible custom packing or encryption.")

    # Static
    if arch in ("x86-64", "i386", "arm", "aarch64", "mips"):
        if symbols:
            steps.append("Disassemble key functions (main, check_*, validate) with objdump -d or Ghidra.")
        else:
            steps.append("Binary is stripped. Use Ghidra or radare2 to locate entry and main heuristically.")

    # Dynamic
    if arch in ("x86-64", "i386"):
        steps.append("Run under ltrace/strace to observe library calls and syscalls.")
        steps.append("Set gdb breakpoints on strcmp/memcmp to capture expected values at runtime.")

    if not steps:
        steps.append("Manual analysis required — examine with Ghidra or IDA.")

    return steps


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

class RevChecker:
    """CTF Rev binary triage analyzer."""

    def __init__(self, path: str):
        self.path = path
        self.result: Optional[RevResult] = None

    def run(self) -> RevResult:
        # Read the binary once and pass to all functions that need it
        try:
            data = Path(self.path).read_bytes()
        except OSError:
            data = b""

        # Run independent subprocess calls in parallel
        with ThreadPoolExecutor(max_workers=3) as executor:
            future_file_info = executor.submit(identify_file, self.path)
            future_sections = executor.submit(section_entropies, self.path, data)
            future_symbols = executor.submit(check_symbols, self.path)

            # Collect results with graceful error handling
            try:
                file_info = future_file_info.result()
            except Exception:
                file_info = "unknown (file command failed)"

            try:
                sections = future_sections.result()
            except Exception:
                sections = []

            try:
                symbols = future_symbols.result()
            except Exception:
                symbols = False

        # Process results that depend on file_info or data
        arch = parse_architecture(file_info)
        packer = detect_packer(data) if data else None
        ent_suspect = has_entropy_suspect(sections)
        interesting = extract_interesting_strings(data) if data else []
        rec = recommend_next(file_info, arch, packer, ent_suspect, symbols, interesting)

        self.result = RevResult(
            file_info=file_info,
            architecture=arch,
            packer_detected=packer,
            entropy_suspect=ent_suspect,
            interesting_strings=interesting,
            symbols_present=symbols,
            recommended_next=rec,
            sections=sections,
        )
        return self.result

    def print_report(self):
        if not self.result:
            self.run()
        r = self.result

        print("=" * 60)
        print("REV BINARY TRIAGE REPORT")
        print("=" * 60)

        print(f"\n[FILE INFO]\n  {r.file_info}")
        print(f"\n[ARCHITECTURE]\n  {r.architecture}")

        print(f"\n[PACKER]")
        if r.packer_detected:
            print(f"  Detected: {r.packer_detected}")
        else:
            print("  None detected")

        print(f"\n[ENTROPY]")
        if r.sections:
            for sec in r.sections:
                tag = " <<<" if sec.get("entropy", 0) >= 7.0 else ""
                print(f"  {sec['name']:20s}  entropy={sec['entropy']:.2f}  "
                      f"size={sec['size']}{tag}")
        if r.entropy_suspect:
            print("  *** Suspicious high entropy detected ***")

        print(f"\n[INTERESTING STRINGS]")
        if r.interesting_strings:
            for s in r.interesting_strings[:10]:
                print(f"  - {s}")
        else:
            print("  (none found)")

        print(f"\n[SYMBOLS]")
        print(f"  Present: {'Yes' if r.symbols_present else 'No (stripped)'}")

        print(f"\n[RECOMMENDED NEXT STEPS]")
        for i, step in enumerate(r.recommended_next, 1):
            print(f"  {i}. {step}")

        print("\n" + "=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Rev Binary Triage — Identify, Unpack, and Trace",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python3 rev_check.py ./crackme
    python3 rev_check.py ./crackme --output recon.json
        """,
    )
    parser.add_argument("file", help="Target binary file")
    parser.add_argument("--output", "-o", help="Write JSON summary to this path")

    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"Error: file not found: {args.file}", file=sys.stderr)
        return 1

    checker = RevChecker(args.file)
    checker.run()
    checker.print_report()

    if args.output:
        with open(args.output, "w") as fh:
            json.dump(asdict(checker.result), fh, indent=2, default=str)
        print(f"\n[+] JSON saved to: {args.output}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
