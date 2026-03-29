---
name: network-search-ddg
description: Search the web using DuckDuckGo when Claude Code's built-in WebSearch tool is unavailable or insufficient. Use for CTF research, documentation lookup, exploit techniques, CVE details, or tool manuals.
---

# DuckDuckGo Network Search

Use this skill to perform web searches via DuckDuckGo when you need external information but the built-in WebSearch tool is not available or returns insufficient results.

## When to Use

- WebSearch tool is unavailable or rate-limited
- Need to search for CTF-specific techniques or writeups
- Looking up CVE details, exploit explanations, or tool documentation
- Researching programming language quirks or library behaviors
- Finding syntax references or configuration examples

## Quick Start

```bash
# Basic search (returns top 10 results)
python3 .claude/skills/network-search-ddg/scripts/ddg_search.py "python pickle deserialization RCE"

# Search with result limit
python3 .claude/skills/network-search-ddg/scripts/ddg_search.py "CVE-2024-XXXX nginx" --limit 5

# Save results to file for reference
python3 .claude/skills/network-search-ddg/scripts/ddg_search.py "glibc malloc exploitation" --output research.md
```

## Search Tips

### Effective Queries

| Goal | Query Pattern | Example |
|------|--------------|---------|
| CTF Writeup | `<challenge name> ctf writeup` | `corCTF 2024 web writeup` |
| CVE Details | `CVE-XXXX-XXXX <component>` | `CVE-2021-44228 log4j` |
| Technique | `<technique> exploitation guide` | `protobuf deserialization exploitation guide` |
| Tool Manual | `<tool> command examples` | `ffuf recursion command examples` |
| Payload | `<target> payload cheat sheet` | `jwt none algorithm payload` |

### Escaping Special Characters

Wrap queries in quotes to handle special characters:

```bash
python3 .claude/skills/network-search-ddg/scripts/ddg_search.py '"SQL injection" "boolean blind" sqlite'
python3 .claude/skills/network-search-ddg/scripts/ddg_search.py "bash reverse shell one-liner"
```

## Workflow

1. **Identify the information need**
   - What specific knowledge gap are you trying to fill?
   - Is it a CVE, a technique, a tool, or a syntax reference?

2. **Formulate the query**
   - Use specific keywords that would appear in technical documentation
   - Include version numbers or years for recent vulnerabilities
   - Add "CTF" or "writeup" for challenge-specific information

3. **Execute the search**
   - Start with `--limit 5` for quick checks
   - Increase to `--limit 10` or more for research tasks

4. **Process results**
   - Review titles and snippets for relevance
   - Open promising URLs manually if deeper reading needed
   - Save results to file when researching complex topics

5. **Iterate if needed**
   - Refine query with more specific terms
   - Try alternative phrasings (e.g., "bypass" vs "waf evasion")

## Integration with CTF Workflow

### During Recon
```bash
# Research unknown technology
python3 .claude/skills/network-search-ddg/scripts/ddg_search.py "what is <suspicious_header_value> framework"
```

### During Exploitation
```bash
# Look up specific technique
python3 .claude/skills/network-search-ddg/scripts/ddg_search.py "nodejs vm2 sandbox escape 2023"
```

### For Knowledge Capture
```bash
# Document findings
python3 .claude/skills/network-search-ddg/scripts/ddg_search.py "<technique> mitigation strategies" --output notes.md
```

## Limitations

- DuckDuckGo may rate-limit aggressive automated queries
- Some results may be JavaScript-heavy sites that won't render properly
- No built-in result caching; repeated identical searches may be throttled
- Search operators (site:, filetype:) have limited support via lite interface

## Fallback Options

If DuckDuckGo search fails:

1. Try `curl` directly to specific documentation sites you know
2. Use `wget` to fetch raw pages if you know the URL
3. Search GitHub directly: `curl -s "https://api.github.com/search/repositories?q=<query>"`

## Script Dependencies

The helper script requires:
- Python 3.6+
- `requests` library (install with `pip3 install requests`)
- `beautifulsoup4` library (install with `pip3 install beautifulsoup4`)

Install dependencies:
```bash
pip3 install requests beautifulsoup4
```

## Maintenance

Keep queries focused and specific. The DuckDuckGo lite interface works best for:
- Finding documentation and manuals
- Locating CVE references
- Discovering CTF writeups and techniques
- Looking up syntax and examples
