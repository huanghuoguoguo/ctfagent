---
name: pwn-initial-recon
description: Binary analysis and reconnaissance for CTF pwn challenges. Use when encountering ELF binaries, shared libraries, or unknown executables to identify protection mechanisms, libc versions, vulnerability classes, and exploitation strategies.
---

# Pwn Initial Recon

Systematic binary analysis for CTF pwn challenges. Quickly determine what protections are in place, what vulnerabilities exist, and what exploitation strategy to pursue.

## When to Use

- First encountering a pwn challenge binary
- Analyzing attached ELF files or shared libraries
- Determining if a binary is exploitable and how
- Before writing any exploit code

## Quick Start

```bash
# Full binary analysis
python3 .claude/skills/pwn-initial-recon/scripts/pwn_check.py --file ./chall

# With libc for version analysis
python3 .claude/skills/pwn-initial-recon/scripts/pwn_check.py --file ./chall --libc ./libc.so.6

# Check remote target (if provided)
python3 .claude/skills/pwn-initial-recon/scripts/pwn_check.py --file ./chall --host target.com --port 1337

# Export analysis for exploit development
python3 .claude/skills/pwn-initial-recon/scripts/pwn_check.py --file ./chall --output analysis.json
```

## Analysis Checklist

### 1. File Identification

```bash
# Basic file info
file ./chall
strings ./chall | head -20

# Via script
python3 .claude/skills/pwn-initial-recon/scripts/pwn_check.py --file ./chall --check file
```

**Key information:**
- Architecture (x86/x64/ARM/MIPS)
- Bit-ness (32/64-bit)
- Stripped or not (symbols available?)
- Statically or dynamically linked

### 2. Protection Mechanisms (checksec)

| Protection | Check | Impact on Exploitation |
|------------|-------|----------------------|
| **NX** (No-eXecute) | Stack/heap not executable | Need ROP/shellcode on heap |
| **Canary** | Stack cookie | Need leak or bypass before overflow |
| **PIE** (Position Independent) | Base address randomized | Need leak or brute-force base |
| **RELRO** (Relocation Read-Only) | GOT write protection | Full RELRO: can't overwrite GOT; Partial: can |
| **FORTIFY** | Buffer check functions | Harder stack overflows |

```bash
# Full checksec
python3 .claude/skills/pwn-initial-recon/scripts/pwn_check.py --file ./chall --check protections

# Or use pwnkit/pwn checksec
pwn checksec ./chall
```

**Decision matrix:**

| NX | Canary | PIE | RELRO | Strategy |
|----|--------|-----|-------|----------|
| ✗ | ✗ | ✗ | None | ret2shellcode |
| ✓ | ✗ | ✗ | None | ret2system/ROP |
| ✓ | ✓ | ✗ | None | Leak canary → overflow → ret2system |
| ✓ | ✓ | ✓ | Full | Leak base → leak canary → ROP or one_gadget |

### 3. Libc Analysis

```bash
# Identify libc version
python3 .claude/skills/pwn-initial-recon/scripts/pwn_check.py --libc ./libc.so.6

# Or manual check
strings ./libc.so.6 | grep "^GLIBC_2\."
readelf -s ./libc.so.6 | grep " __libc_start_main"
```

**Key symbols to identify:**
- `__libc_start_main` - Version indicator
- `system` - For ret2system
- `/bin/sh` - String offset
- `__free_hook` / `__malloc_hook` - For heap exploits
- `one_gadget` offsets - For constraint-based code execution

**Online libc database:**
- https://libc.blukat.me/
- https://libc.rip/

### 4. Vulnerability Detection

```bash
# Scan for dangerous functions
python3 .claude/skills/pwn-initial-recon/scripts/pwn_check.py --file ./chall --check vulnerabilities
```

**Dangerous functions:**

| Function | Vulnerability | Exploitation |
|----------|--------------|--------------|
| `gets()` | Unbounded read | Stack overflow |
| `strcpy()` | No length check | Stack overflow |
| `sprintf()` | Format string | Info leak / Write |
| `printf(user_input)` | Format string | Info leak / Arbitrary write |
| `read(0, buf, large)` | Overflow if buf small | Stack/Heap overflow |
| `scanf("%s", buf)` | No length limit | Stack overflow |
| `free(ptr)` (UAF) | Use after free | Heap corruption |
| `strcat()` | Buffer overflow | Stack overflow |

### 5. Symbol Analysis

```bash
# Check available symbols
nm ./chall | grep -E " T | B "
readelf -s ./chall | grep FUNC

# Look for useful symbols
- win()/flag()/get_shell() - Target function
- backdoor/system - Existing gadgets
- print_flag/format_string - Helper functions
```

### 6. String Analysis

```bash
# Check for interesting strings
strings ./chall | grep -E "(flag|/bin/sh|password|key)"

# Check format string patterns
strings ./chall | grep "%"
```

## Exploitation Strategy Guide

### Strategy 1: ret2shellcode
**Conditions:** NX disabled, stack executable
```python
# Fill buffer + shellcode + jump to shellcode
payload = b"A"*offset + shellcode + b"A"*(ret_offset-len(shellcode)) + jmp_esp
```

### Strategy 2: ret2system
**Conditions:** NX enabled, PIE disabled, system@plt available
```python
# ROP: pop rdi; addr("/bin/sh"); system
payload = b"A"*offset + p64(pop_rdi) + p64(bin_sh_addr) + p64(system_plt)
```

### Strategy 3: ROP chain
**Conditions:** NX enabled, no system, need gadgets
```python
# ROP: syscall execve("/bin/sh", 0, 0)
rop = ROP(binary)
rop.execve(bin_sh_addr, 0, 0)
payload = b"A"*offset + rop.chain()
```

### Strategy 4: one_gadget
**Conditions:** PIE enabled, need simple RCE
```python
# Find one_gadget with constraints
# one_gadget ./libc.so.6
payload = b"A"*offset + p64(canary) + b"A"*8 + p64(one_gadget_offset)
```

### Strategy 5: Format String
**Conditions:** printf(user_input) found
```python
# Leak: %p.%p.%p
# Write: %<offset>$n to overwrite GOT
```

### Strategy 6: Heap Exploitation
**Conditions:** malloc/free present, heap operations
```python
# UAF: Use after free
# Double free: Free same chunk twice
# Fastbin dup: Corrupt fastbin fd
# Tcache poisoning: Tcache fd overwrite
```

## Workflow

1. **Run initial recon**
   ```bash
   python3 .claude/skills/pwn-initial-recon/scripts/pwn_check.py --file ./chall --libc ./libc.so.6
   ```

2. **Analyze output**
   - Identify protection bypass requirements
   - Note available attack vectors
   - Determine if leaks are needed

3. **Plan exploit**
   - Choose strategy based on protections
   - Identify required primitives (leak/write/control flow)
   - Map out ROP chain or heap layout

4. **Develop exploit**
   - Start with basic skeleton
   - Test locally first
   - Adjust offsets for remote if needed

## Output Format

The recon script outputs:

```json
{
  "file": {
    "path": "./chall",
    "arch": "x86-64",
    "bits": 64,
    "endian": "little",
    "stripped": false,
    "static": false
  },
  "protections": {
    "nx": true,
    "canary": true,
    "pie": true,
    "relro": "full",
    "fortify": false
  },
  "libc": {
    "version": "2.31",
    "path": "./libc.so.6",
    "symbols": {
      "system": 0x12345,
      "/bin/sh": 0x67890
    }
  },
  "vulnerabilities": [
    {
      "type": "overflow",
      "function": "gets",
      "location": "0x401234"
    }
  ],
  "strategy": "Leak canary via format string, then ret2system",
  "symbols": {
    "win": null,
    "backdoor": "0x401337"
  }
}
```

## Integration with Exploit Development

```python
# Use recon output in exploit
import json

with open('analysis.json') as f:
    info = json.load(f)

# Auto-configure exploit
context.arch = info['file']['arch']
context.bits = info['file']['bits']

if info['protections']['pie']:
    # Need leak
    pass

if info['protections']['canary']:
    # Need canary leak
    pass
```

## Tools Required

- `pwntools` - Python exploit development
- `checksec` / `pwn checksec` - Protection detection
- `file` / `binutils` - Binary analysis
- `one_gadget` - One gadget finder
- `ROPgadget` / `ropper` - ROP chain building
- `libc-database` - Libc identification

## References

- [Pwntools Documentation](https://docs.pwntools.com/)
- [CTF Wiki - Pwn](https://ctf-wiki.org/pwn/)
- [One Gadget](https://github.com/david942j/one_gadget)
- [ROP Gadget](https://github.com/JonathanSalwan/ROPgadget)
- [Libc Database](https://libc.blukat.me/)
