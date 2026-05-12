---
name: pwn-triage
description: Router for binary exploitation triage. Use when encountering ELF binaries, shared libraries, or unknown executables. Routes through initial recon, leak strategy (if canary/PIE), and exploit scaffold generation.
---

# Pwn Triage

Unified binary exploitation triage workflow. Routes through reconnaissance, protection bypass, and exploit development based on what protections are present.

## When to Use

- First encountering a pwn challenge binary
- Analyzing attached ELF files or shared libraries
- Need to develop a stack-based exploit

## Workflow

```
┌─────────────────┐
│ initial-recon   │  →  Protections? Vulnerabilities? Strategy?
└────────┬────────┘
         │
    ┌────▼────┐
    │ Canary? │──Yes──→ canary-pie (leak strategy)
    │   PIE?  │──Yes──→ canary-pie (leak strategy)
    └────┬────┘
         │ No
    ┌────▼────────────┐
    │ stack-overflow  │  →  ret2win / ret2libc / generic scaffold
    └─────────────────┘
```

## Routing Table

| Recon Output | Route To |
|--------------|----------|
| Canary enabled or PIE enabled | `canary-pie` reference |
| No canary, no PIE, stack overflow found | `stack-overflow` reference |
| Heap-based vulnerability | Consider other skills |
| Format string primary vector | Consider format-string skills |

## Quick Start

1. Run initial recon:
   ```bash
   python3 src/tools/pwn/pwn_check.py --file ./chall --output analysis.json
   ```

2. Check `analysis.json` for protections:
   ```bash
   cat analysis.json | jq '.protections'
   ```

3. Route based on protections:
   - Canary or PIE enabled → See `references/canary-pie.md`
   - No protections → See `references/stack-overflow.md`

## Tool Reference

All tools are in `src/tools/pwn/`:

| Tool | Purpose |
|------|---------|
| `pwn_check.py` | Full binary analysis (file, protections, libc, vulnerabilities) |
| `exploit_scaffold.py` | Generate ret2win/ret2libc/generic exploit skeleton |
| `leak_scaffold.py` | Generate leak + exploit for canary/PIE bypass |

### pwn_check.py

```bash
# Full analysis
python3 src/tools/pwn/pwn_check.py --file ./chall --output analysis.json

# With libc
python3 src/tools/pwn/pwn_check.py --file ./chall --libc ./libc.so.6

# Individual checks
python3 src/tools/pwn/pwn_check.py --file ./chall --check file
python3 src/tools/pwn/pwn_check.py --file ./chall --check protections
python3 src/tools/pwn/pwn_check.py --file ./chall --check vulnerabilities
```

### exploit_scaffold.py

```bash
# Auto-detect template from analysis
python3 src/tools/pwn/exploit_scaffold.py --analysis analysis.json --output exploit.py

# Force specific template
python3 src/tools/pwn/exploit_scaffold.py --analysis analysis.json --template ret2libc --output exploit.py
```

### leak_scaffold.py

```bash
# Auto-select based on protections
python3 src/tools/pwn/leak_scaffold.py --analysis analysis.json --output exploit.py

# Override strategy
python3 src/tools/pwn/leak_scaffold.py --analysis analysis.json --template canary_fmtstr --output exploit.py
```

## Protection Decision Matrix

| NX | Canary | PIE | RELRO | Strategy |
|----|--------|-----|-------|----------|
| ✗ | ✗ | ✗ | None | ret2shellcode |
| ✓ | ✗ | ✗ | None | ret2system/ROP |
| ✓ | ✓ | ✗ | None | Leak canary → overflow → ret2system |
| ✓ | ✓ | ✓ | Full | Leak base → leak canary → ROP or one_gadget |

## References

- [`references/initial-recon.md`](references/initial-recon.md) - Full recon checklist and analysis output
- [`references/stack-overflow.md`](references/stack-overflow.md) - ret2win/ret2libc/generic exploit development
- [`references/canary-pie.md`](references/canary-pie.md) - Leak strategies and combined exploit scaffold

## Exit Conditions

Switch to other skills when:
- Primary vulnerability is heap-based (UAF, double-free, tcache)
- Format string is the primary exploitation path, not just a leak tool
- Binary is statically linked with no interesting gadgets (manual ROP needed)
