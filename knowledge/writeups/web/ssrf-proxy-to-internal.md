---
title: "SSRF Proxy to Internal Host"
category: web
slug: ssrf-proxy-to-internal
created: 2026-03-28
status: solved
tags:
  - ssrf
  - internal-host
  - proxy
doc_kind: writeup
---
# SSRF Proxy to Internal Host

## Challenge Summary

- Source: Local CTF lab (SSRF Lab)
- Target: http://localhost:5000/proxy
- Goal: Access internal host to retrieve flag

## Initial Signals

- Entry point: `/proxy?url=` endpoint
- Visible hints: "SSRF Lab Vulnerable Front-end", mentions `/proxy?url=http://example.com`
- First confirming probe: `?url=http://127.0.0.1` returned connection refused error (proving server-side fetch)

## Exploit Chain

1. **Verify SSRF** - Tested `?url=http://127.0.0.1`, confirmed server-side request
2. **Try file://** - Blocked ("No connection adapters were found")
3. **Test internal hostname** - Direct access to `?url=http://internal` returned flag immediately

## Key Evidence

- Endpoint fetches URLs server-side (Python requests library)
- `file://` protocol not supported (requests library limitation)
- Internal hostname `internal` resolves to internal service containing flag
- No additional hops required - direct access succeeded

## Dead Ends

- Attempted `file:///etc/passwd` - protocol not supported
- Attempted `http://127.0.0.1` - connection refused (different service on internal)

## Payloads And Commands

```bash
# Verify SSRF (connection refused but proves server-side fetch)
curl "http://localhost:5000/proxy?url=http://127.0.0.1"

# Direct access to internal host - immediate flag
curl "http://localhost:5000/proxy?url=http://internal"
```

## Flag / Outcome

- Flag: `CTF{ssrf_successful_exploration_2026}`

## Reusable Lessons

- In Docker/container environments, hostnames like `internal` commonly point to sibling containers
- SSRF may not require complex chains - sometimes direct internal access works
- `file://` blocked doesn't prevent `http://internal` from working
- Always test common internal hostnames: `internal`, `backend`, `api`, `db`, `localhost`

## Pattern Candidates

- Existing pattern to update: `ssrf-to-lfi-to-localhost-rce` - add note about internal hostnames
- New pattern worth creating: Container environment SSRF - common internal hostnames in Docker Compose setups
