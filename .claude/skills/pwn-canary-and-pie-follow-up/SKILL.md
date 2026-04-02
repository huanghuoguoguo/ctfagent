---
name: pwn-canary-and-pie-follow-up
description: Bridge pwn-initial-recon and pwn-stack-overflow-exploit-dev when canary and/or PIE is enabled. Use after recon shows these protections on a stack-based vulnerability to determine the leak strategy and generate a combined exploit skeleton.
---

# Pwn Canary and PIE Follow-Up

Use this skill after `pwn-initial-recon` when the binary has canary and/or PIE enabled and the vulnerability is still stack-based. It fills the gap before `pwn-stack-overflow-exploit-dev` by determining how to leak the values that the basic scaffold assumes are absent.

Treat it as a short SOP:

- identify which protections need bypassing
- probe for leak primitives in priority order
- choose the cheapest bypass strategy
- scaffold the combined leak-then-exploit script

## When to Use

- `pwn-initial-recon` reports canary and/or PIE enabled
- The vulnerability class is a stack overflow (gets, strcpy, read into small buf, etc.)
- You need a leak strategy before a basic exploit scaffold is meaningful

## When NOT to Use

- Neither canary nor PIE is enabled -- go straight to `pwn-stack-overflow-exploit-dev`
- The primary vulnerability is heap-based (UAF, double-free, tcache poisoning)
- Format string is the *primary exploitation vector*, not just a leak tool
- The binary is statically linked with no interesting gadgets (manual ROP needed)

## Quick Start

```bash
# Run recon first
python3 .claude/skills/pwn-initial-recon/scripts/pwn_check.py \
  --file ./chall --output analysis.json

# Generate a leak + exploit skeleton
python3 .claude/skills/pwn-canary-and-pie-follow-up/scripts/leak_scaffold.py \
  --analysis analysis.json --output exploit.py
```

Override the leak strategy:

```bash
python3 .claude/skills/pwn-canary-and-pie-follow-up/scripts/leak_scaffold.py \
  --analysis analysis.json --template canary_bruteforce --output exploit.py
```

## Probe Order -- Canary Bypass

Try these in order. Stop at the first viable primitive.

1. **Format string leak** -- `printf(user_input)` present? Leak canary from stack with `%<offset>$p`.
2. **Partial overwrite** -- Can you overwrite only the LSB of the return address without touching the canary? If so, skip canary entirely.
3. **Brute-force (forking server)** -- Does the server fork per connection? Canary stays the same across forks; guess one byte at a time (256 tries per byte, 3 unknown bytes on 64-bit because LSB is `\x00`).
4. **Info leak via output functions** -- Does the binary `puts`/`write` a stack buffer that can be extended past the canary via a controlled size or missing null terminator?
5. **Auxiliary leak** -- Can `/proc/self/maps` or the ELF auxiliary vector be read? Rare but check if the binary opens files from user input.

Decision: if none of these work, re-evaluate whether the vulnerability is really stack-based. Consider heap or format-string skills instead.

## Probe Order -- PIE Bypass

1. **Partial overwrite** -- The low 12 bits of any code address are fixed (page-aligned). Overwriting 1-2 bytes of a return address can redirect within the same page without knowing the base.
2. **Info leak via output functions** -- `puts`/`printf` leaking a `.text` or `.got.plt` address? Subtract the known offset to recover PIE base.
3. **Format string leak** -- Leak a saved return address from the stack with `%<offset>$p`, then compute PIE base.
4. **Fixed-address regions** -- On old kernels, `vsyscall` (0xffffffffff600000) is mapped at a fixed address. Useful as a single-gadget trampoline but rarely sufficient alone.

Decision: if the only viable primitive is partial overwrite and it reaches a win function, hand off to `pwn-stack-overflow-exploit-dev` with the partial overwrite approach.

## Combined Strategy (Canary + PIE)

When both are enabled, chain leaks in this order:

1. **Leak canary** -- usually cheaper because the canary is closer to the buffer on the stack.
2. **Leak a code address** -- a saved return address gives PIE base (subtract the known offset such as `__libc_start_main+XX` or `main+XX`).
3. **Optionally leak a libc address** -- if the ROP target is `system` or a one_gadget in libc, leak a GOT entry after computing PIE base.
4. **Build final payload** -- `padding + canary + saved_rbp + rop_chain`.

The scaffold script automates step 4 once you supply concrete leak values or leak functions.

## Offset Discipline

Do not guess offsets. Use:

```bash
python3 -c 'from pwn import *; print(cyclic(200))'
python3 -c 'from pwn import *; print(cyclic_find(0x61616174))'
```

For canary offset specifically, the canary sits right after the local buffer. In GDB:

```
b *vuln+<ret_instruction_offset>
x/20gx $rsp
```

Look for the 8-byte value ending in `\x00` (the canary null byte is the LSB on little-endian).

## Workflow

1. Run `pwn-initial-recon` and confirm canary/PIE in `analysis.json`.
2. Walk the canary probe order above. Note which primitive works.
3. Walk the PIE probe order above. Note which primitive works.
4. Generate the scaffold:
   ```bash
   python3 .claude/skills/pwn-canary-and-pie-follow-up/scripts/leak_scaffold.py \
     --analysis analysis.json --output exploit.py
   ```
5. Fill in leak offsets and test locally.
6. Once the leak is stable, the payload section follows `pwn-stack-overflow-exploit-dev` patterns.
7. Save the case with `ctf-knowledge-capture`.

## Template Choice

The scaffold script selects automatically:

| Canary | PIE | Template |
|--------|-----|----------|
| yes | no | `canary_fmtstr` or `canary_bruteforce` |
| no | yes | `pie_leak` |
| yes | yes | `combined` |

Override with `--template <name>`.

## Exit Conditions

Switch away from this skill when:

- format string is the *primary* exploitation path, not just a leak tool -- use a format-string skill
- the vulnerability is heap-based -- wrong skill entirely
- partial overwrite alone reaches a win function -- hand off to `pwn-stack-overflow-exploit-dev`
- no leak primitive exists and brute-force is infeasible -- re-evaluate the vulnerability class
