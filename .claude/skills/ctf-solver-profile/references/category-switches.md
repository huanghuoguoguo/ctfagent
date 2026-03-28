# Category Switching Cues

Use this file when the initial classification is weak.

## Web -> Backdoor / RCE

Look here when:

- the page is blank or nearly blank
- a very small number of parameters exist
- old PHP versions are present
- source suffixes like `.phps` or debug leftovers appear

Cheap probes:

- short parameter names
- `phpinfo();`
- `sleep(3);`
- simple file reads

## Web -> SSRF / source-read

Look here when:

- one input resembles a fetcher, previewer, or URL reader
- responses embed fetched content
- internal or localhost wording appears

Cheap probes:

- external URL fetch
- `file://`
- app source read

## Web -> LFI

Look here when:

- parameters smell like `file`, `page`, `lang`, `template`, `include`
- stack traces or warnings imply include paths
- wrapper behavior differs

Cheap probes:

- `../../`
- double-encoding
- wrapper reads

## Binary -> Pwn

Look here when:

- remote socket service exists
- malformed input changes process behavior
- protections and memory layout matter

Cheap probes:

- `file`
- `checksec`
- `strings`
- crash reproduction

## Binary -> Rev

Look here when:

- there is no live network surface
- challenge behavior is local and deterministic
- logic extraction matters more than memory corruption

Cheap probes:

- strings
- functions
- control-flow landmarks

## Text / Data -> Crypto or Encoding

Look here when:

- content has constrained alphabets
- structure suggests base encodings, XOR, block boundaries, or classical ciphers
- there is no executable surface at all

Cheap probes:

- alphabet analysis
- byte frequency
- length and padding checks
