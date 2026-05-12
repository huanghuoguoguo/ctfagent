#!/usr/bin/env python3
"""
Pwn Binary Initial Reconnaissance
Analyze ELF binaries for CTF pwn challenges.

Usage:
    python3 pwn_check.py --file ./chall
    python3 pwn_check.py --file ./chall --libc ./libc.so.6
    python3 pwn_check.py --file ./chall --output analysis.json
"""

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple


@dataclass
class FileInfo:
    path: str
    arch: str
    bits: int
    endian: str
    stripped: bool
    static: bool
    interpreter: Optional[str] = None


@dataclass
class Protections:
    nx: bool
    canary: bool
    pie: bool
    relro: str  # 'none', 'partial', 'full'
    fortify: bool
    rpath: bool
    runpath: bool


@dataclass
class SymbolInfo:
    name: str
    address: int
    type: str


@dataclass
class Vulnerability:
    type: str
    function: str
    location: Optional[str] = None
    description: Optional[str] = None


@dataclass
class LibcInfo:
    version: Optional[str] = None
    path: Optional[str] = None
    symbols: Dict[str, int] = None
    one_gadgets: List[int] = None


@dataclass
class ReconResult:
    file: FileInfo
    protections: Protections
    libc: Optional[LibcInfo]
    vulnerabilities: List[Vulnerability]
    interesting_strings: List[str]
    symbols: Dict[str, int]
    strategy: str


class PwnChecker:
    """CTF Pwn binary analyzer."""

    DANGEROUS_FUNCTIONS = {
        'gets': 'Unbounded read - stack overflow',
        'strcpy': 'No length check - buffer overflow',
        'sprintf': 'Format string vulnerability',
        'scanf': 'No length limit with %s - overflow',
        'strcat': 'Buffer overflow',
        'memcpy': 'Potential overflow',
        'read': 'Check buffer size vs read size',
        'printf': 'Format string if user controls format',
        'fprintf': 'Format string if user controls format',
        'syslog': 'Format string',
        'free': 'Check for UAF/double-free',
        'malloc': 'Check for heap vulnerabilities',
    }

    def __init__(self, file_path: str, libc_path: Optional[str] = None):
        self.file_path = file_path
        self.libc_path = libc_path
        self.result = None

    def run(self) -> ReconResult:
        """Run full analysis."""
        file_info = self._analyze_file()
        protections = self._check_protections()
        libc_info = self._analyze_libc() if self.libc_path else None
        vulnerabilities = self._find_vulnerabilities()
        strings = self._find_interesting_strings()
        symbols = self._find_binary_symbols()
        strategy = self._determine_strategy(file_info, protections, vulnerabilities)

        self.result = ReconResult(
            file=file_info,
            protections=protections,
            libc=libc_info,
            vulnerabilities=vulnerabilities,
            interesting_strings=strings,
            symbols=symbols,
            strategy=strategy
        )
        return self.result

    def _analyze_file(self) -> FileInfo:
        """Analyze basic file information."""
        # Use file command
        try:
            output = subprocess.run(
                ['file', '-b', self.file_path],
                capture_output=True,
                text=True
            ).stdout.strip()
        except:
            output = ""

        # Parse architecture
        arch = 'unknown'
        bits = 64
        endian = 'little'

        if 'x86-64' in output or '64-bit' in output:
            arch = 'x86-64'
            bits = 64
        elif 'Intel 80386' in output or '32-bit' in output:
            arch = 'i386'
            bits = 32
        elif 'ARM' in output or 'aarch64' in output:
            arch = 'aarch64' if '64' in output else 'arm'
            bits = 64 if '64' in output else 32
        elif 'MIPS' in output:
            arch = 'mips'
            endian = 'big' if 'MSB' in output else 'little'

        # Check if stripped
        stripped = 'stripped' in output

        # Check if statically linked
        static = 'statically linked' in output

        # Get interpreter
        interpreter = None
        try:
            readelf = subprocess.run(
                ['readelf', '-l', self.file_path],
                capture_output=True,
                text=True
            ).stdout
            match = re.search(r'interpreter:\s*(.+?)]', readelf)
            if match:
                interpreter = match.group(1)
        except:
            pass

        return FileInfo(
            path=self.file_path,
            arch=arch,
            bits=bits,
            endian=endian,
            stripped=stripped,
            static=static,
            interpreter=interpreter
        )

    def _check_protections(self) -> Protections:
        """Check binary protections using checksec or manual analysis."""
        # Try checksec first
        try:
            output = subprocess.run(
                ['checksec', '--file=' + self.file_path, '--output=json'],
                capture_output=True,
                text=True
            ).stdout
            if output:
                import json
                data = json.loads(output)
                if self.file_path in data:
                    info = data[self.file_path]
                    return Protections(
                        nx=info.get('nx', 'enabled') == 'enabled',
                        canary=info.get('canary', 'no') == 'yes',
                        pie=info.get('pie', 'no') != 'no',
                        relro=info.get('relro', 'no').lower(),
                        fortify=info.get('fortify_source', 'no') == 'yes',
                        rpath=info.get('rpath', 'no') == 'yes',
                        runpath=info.get('runpath', 'no') == 'yes'
                    )
        except:
            pass

        # Try pwn checksec
        try:
            output = subprocess.run(
                ['pwn', 'checksec', self.file_path],
                capture_output=True,
                text=True
            ).stdout
            return self._parse_checksec_output(output)
        except:
            pass

        # Manual analysis
        return self._manual_protections_check()

    def _parse_checksec_output(self, output: str) -> Protections:
        """Parse checksec output."""
        nx = 'NX enabled' in output or 'NX:       Enabled' in output
        canary = 'Canary found' in output or 'Canary:   Enabled' in output
        pie = 'PIE enabled' in output or 'PIE:      Enabled' in output
        fortify = 'FORTIFY' in output and 'enabled' in output.lower()

        relro = 'no'
        if 'Full RELRO' in output or 'RELRO:    Full' in output:
            relro = 'full'
        elif 'Partial RELRO' in output or 'RELRO:    Partial' in output:
            relro = 'partial'

        return Protections(
            nx=nx,
            canary=canary,
            pie=pie,
            relro=relro,
            fortify=fortify,
            rpath='RPATH' in output,
            runpath='RUNPATH' in output
        )

    def _manual_protections_check(self) -> Protections:
        """Manual protection analysis using readelf."""
        try:
            # Check RELRO
            readelf_h = subprocess.run(
                ['readelf', '-h', self.file_path],
                capture_output=True,
                text=True
            ).stdout

            relro = 'no'
            if 'GNU_RELRO' in readelf_h:
                readelf_d = subprocess.run(
                    ['readelf', '-d', self.file_path],
                    capture_output=True,
                    text=True
                ).stdout
                if 'BIND_NOW' in readelf_d:
                    relro = 'full'
                else:
                    relro = 'partial'

            # Check NX (GNU_STACK)
            readelf_l = subprocess.run(
                ['readelf', '-l', self.file_path],
                capture_output=True,
                text=True
            ).stdout
            nx = 'GNU_STACK' in readelf_l and 'RWE' not in readelf_l

            # Check symbols for canary
            nm = subprocess.run(
                ['nm', self.file_path],
                capture_output=True,
                text=True
            ).stdout
            canary = '__stack_chk_fail' in nm or '__stack_chk_guard' in nm

            # Check PIE
            pie = 'DYN' in readelf_h and 'debug' not in readelf_h

            return Protections(
                nx=nx,
                canary=canary,
                pie=pie,
                relro=relro,
                fortify=False,
                rpath=False,
                runpath=False
            )
        except:
            return Protections(
                nx=True, canary=False, pie=False, relro='no',
                fortify=False, rpath=False, runpath=False
            )

    def _analyze_libc(self) -> Optional[LibcInfo]:
        """Analyze libc if provided."""
        if not self.libc_path or not os.path.exists(self.libc_path):
            return None

        # Get version
        version = None
        try:
            strings = subprocess.run(
                ['strings', self.libc_path],
                capture_output=True,
                text=True
            ).stdout
            match = re.search(r'GLIBC_(\d+\.\d+)', strings)
            if match:
                version = match.group(1)
        except:
            pass

        # Get key symbols
        symbols = {}
        try:
            nm = subprocess.run(
                ['nm', '-D', self.libc_path],
                capture_output=True,
                text=True
            ).stdout

            for line in nm.split('\n'):
                if 'system' in line or '__libc_start_main' in line or 'str_bin_sh' in line:
                    parts = line.split()
                    if len(parts) >= 3:
                        addr = int(parts[0], 16) if parts[0] else 0
                        name = parts[2]
                        symbols[name] = addr
        except:
            pass

        # Try to get one_gadgets
        one_gadgets = []
        try:
            result = subprocess.run(
                ['one_gadget', self.libc_path],
                capture_output=True,
                text=True
            )
            for line in result.stdout.split('\n'):
                match = re.match(r'([0-9a-fx]+)', line.strip())
                if match:
                    one_gadgets.append(int(match.group(1), 0))
        except:
            pass

        return LibcInfo(
            version=version,
            path=self.libc_path,
            symbols=symbols,
            one_gadgets=one_gadgets[:5] if one_gadgets else None  # Top 5
        )

    def _find_vulnerabilities(self) -> List[Vulnerability]:
        """Find potential vulnerabilities."""
        vulns = []

        # Check for dangerous functions
        try:
            # Use objdump or strings
            output = subprocess.run(
                ['objdump', '-t', self.file_path],
                capture_output=True,
                text=True
            ).stdout

            for func, desc in self.DANGEROUS_FUNCTIONS.items():
                if func in output:
                    vulns.append(Vulnerability(
                        type=self._classify_vulnerability(func),
                        function=func,
                        description=desc
                    ))
        except:
            pass

        # Check for format string patterns
        try:
            strings = subprocess.run(
                ['strings', self.file_path],
                capture_output=True,
                text=True
            ).stdout

            if '%s%s%s' in strings or '%x%x%x' in strings:
                vulns.append(Vulnerability(
                    type='format_string',
                    function='printf',
                    description='Possible format string vulnerability'
                ))
        except:
            pass

        return vulns

    def _classify_vulnerability(self, func: str) -> str:
        """Classify vulnerability type."""
        overflow_funcs = ['gets', 'strcpy', 'strcat', 'scanf', 'memcpy', 'read']
        format_funcs = ['printf', 'sprintf', 'fprintf', 'syslog']
        heap_funcs = ['free', 'malloc', 'calloc', 'realloc']

        if func in overflow_funcs:
            return 'overflow'
        elif func in format_funcs:
            return 'format_string'
        elif func in heap_funcs:
            return 'heap'
        return 'other'

    def _find_interesting_strings(self) -> List[str]:
        """Find interesting strings in binary."""
        interesting = []
        patterns = [
            rb'flag\{[^}]*\}',
            rb'FLAG\{[^}]*\}',
            rb'/bin/sh',
            rb'/bin/bash',
            rb'password',
            rb'Password',
            rb'key',
            rb'welcome',
            rb'congrat',
            rb'WIN',
            rb'success',
        ]

        try:
            with open(self.file_path, 'rb') as f:
                data = f.read()

            for pattern in patterns:
                matches = re.findall(pattern, data)
                for match in matches:
                    try:
                        interesting.append(match.decode('utf-8', errors='ignore'))
                    except:
                        pass
        except:
            pass

        return list(set(interesting))[:10]  # Top 10 unique

    def _find_binary_symbols(self) -> Dict[str, int]:
        """Collect the most useful local, PLT, and GOT symbols for exploit scaffolding."""
        symbols: Dict[str, int] = {}
        wanted_names = {
            'main',
            'vuln',
            'win',
            'backdoor',
            'get_shell',
            'print_flag',
            'pop_rdi_ret',
            'useful_gadget',
            'puts',
            'printf',
            'read',
            'write',
            'gets',
        }

        try:
            nm_output = subprocess.run(
                ['nm', '-C', self.file_path],
                capture_output=True,
                text=True
            ).stdout
            for line in nm_output.splitlines():
                parts = line.split()
                if len(parts) < 3:
                    continue
                if not re.fullmatch(r'[0-9a-fA-F]+', parts[0]):
                    continue
                name = parts[2]
                if name in wanted_names:
                    symbols[name] = int(parts[0], 16)
        except Exception:
            pass

        try:
            objdump_plt = subprocess.run(
                ['objdump', '-d', self.file_path],
                capture_output=True,
                text=True
            ).stdout
            for line in objdump_plt.splitlines():
                match = re.match(r'^\s*([0-9a-fA-F]+)\s+<([^>]+@plt)>:', line)
                if match:
                    symbols[match.group(2)] = int(match.group(1), 16)
        except Exception:
            pass

        try:
            objdump_got = subprocess.run(
                ['objdump', '-R', self.file_path],
                capture_output=True,
                text=True
            ).stdout
            for line in objdump_got.splitlines():
                match = re.search(r'^([0-9a-fA-F]+)\s+R_\S+\s+(.+)$', line.strip())
                if not match:
                    continue
                name = match.group(2).strip()
                if not name.endswith('@got'):
                    name = f'{name}@got'
                symbols[name] = int(match.group(1), 16)
        except Exception:
            pass

        return dict(sorted(symbols.items()))

    def _determine_strategy(self, file_info: FileInfo,
                           protections: Protections,
                           vulnerabilities: List[Vulnerability]) -> str:
        """Determine exploitation strategy."""
        strategies = []

        # Check protections
        if not protections.nx:
            strategies.append("ret2shellcode (NX disabled)")

        if not protections.pie and not protections.canary:
            strategies.append("ret2system/ROP (no PIE/canary)")

        if protections.canary and not protections.pie:
            strategies.append("Leak canary first, then ret2system")

        if protections.pie and protections.canary:
            strategies.append("Leak base address and canary, then ROP")

        # Check vulnerabilities
        for vuln in vulnerabilities:
            if vuln.type == 'format_string':
                strategies.append("Format string for arbitrary read/write")
            elif vuln.type == 'heap':
                strategies.append("Heap exploitation (UAF/double-free)")

        # Check for one_gadget possibility
        if self.libc_path:
            strategies.append("one_gadget for simple RCE")

        if not strategies:
            return "Unknown - manual analysis required"

        return " → ".join(strategies[:2])  # Top 2 strategies

    def print_report(self):
        """Print human-readable report."""
        if not self.result:
            self.run()

        r = self.result

        print("=" * 60)
        print("PWN BINARY RECONNAISSANCE REPORT")
        print("=" * 60)

        print("\n[FILE INFO]")
        print(f"  Path: {r.file.path}")
        print(f"  Architecture: {r.file.arch} ({r.file.bits}-bit)")
        print(f"  Endian: {r.file.endian}")
        print(f"  Stripped: {'Yes' if r.file.stripped else 'No'}")
        print(f"  Static: {'Yes' if r.file.static else 'No'}")
        if r.file.interpreter:
            print(f"  Interpreter: {r.file.interpreter}")

        print("\n[PROTECTIONS]")
        p = r.protections
        print(f"  NX: {'✓ Enabled' if p.nx else '✗ Disabled'}")
        print(f"  Canary: {'✓ Enabled' if p.canary else '✗ Disabled'}")
        print(f"  PIE: {'✓ Enabled' if p.pie else '✗ Disabled'}")
        print(f"  RELRO: {p.relro.upper()}")
        print(f"  FORTIFY: {'✓ Enabled' if p.fortify else '✗ Disabled'}")

        print("\n[VULNERABILITIES]")
        if r.vulnerabilities:
            for v in r.vulnerabilities:
                print(f"  [!] {v.type}: {v.function}")
                if v.description:
                    print(f"      {v.description}")
        else:
            print("  None detected (manual analysis needed)")

        if r.libc:
            print("\n[LIBC INFO]")
            print(f"  Version: {r.libc.version or 'Unknown'}")
            print(f"  Path: {r.libc.path}")
            if r.libc.symbols:
                print("  Symbols:")
                for name, addr in list(r.libc.symbols.items())[:5]:
                    print(f"    {name}: {hex(addr) if addr else 'N/A'}")
            if r.libc.one_gadgets:
                print("  One Gadgets:")
                for addr in r.libc.one_gadgets[:3]:
                    print(f"    {hex(addr)}")

        if r.interesting_strings:
            print("\n[INTERESTING STRINGS]")
            for s in r.interesting_strings[:5]:
                print(f"  - {s}")

        if r.symbols:
            print("\n[SYMBOLS]")
            for name, addr in list(r.symbols.items())[:8]:
                print(f"  {name}: {hex(addr)}")

        print("\n[RECOMMENDED STRATEGY]")
        print(f"  → {r.strategy}")

        print("\n" + "=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description='Pwn Binary Initial Reconnaissance',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python3 pwn_check.py --file ./chall
    python3 pwn_check.py --file ./chall --libc ./libc.so.6
    python3 pwn_check.py --file ./chall --output analysis.json
        """
    )

    parser.add_argument('--file', '-f', required=True,
                       help='Target binary file')
    parser.add_argument('--libc', '-l',
                       help='Path to libc.so.6')
    parser.add_argument('--output', '-o',
                       help='Output JSON file')
    parser.add_argument('--check',
                       choices=['file', 'protections', 'vulns', 'all'],
                       default='all',
                       help='Specific check to run')

    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        return 1

    checker = PwnChecker(args.file, args.libc)
    result = checker.run()

    # Print report
    checker.print_report()

    # Save to file if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(asdict(result), f, indent=2, default=str)
        print(f"\n[+] Analysis saved to: {args.output}")

    return 0


if __name__ == '__main__':
    sys.exit(main())
