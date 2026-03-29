#!/usr/bin/env python3
"""
Serialization Format Detector
Detect Java, Python pickle, and PHP serialization formats.

Usage:
    python3 detect_ser.py --input "base64_or_hex_string" [--verbose]
    python3 detect_ser.py --file input.bin [--verbose]
    python3 detect_ser.py --stdin [--verbose]
"""

import argparse
import base64
import binascii
import re
import sys
from typing import Dict, List, Optional, Tuple


class SerializationDetector:
    """Detect various serialization formats."""

    # Java serialization magic bytes
    JAVA_MAGIC = b'\xac\xed\x00\x05'
    JAVA_MAGIC_ALT = b'\xac\xed'

    # Python pickle protocols
    PICKLE_PROTOCOLS = [b'\x80\x00', b'\x80\x01', b'\x80\x02', b'\x80\x03', b'\x80\x04', b'\x80\x05']

    # Common pickle protocol 4+ base64 prefix
    PICKLE_P4_B64 = 'gASV'
    PICKLE_P5_B64 = 'gASV'

    def __init__(self, data: bytes):
        self.data = data
        self.results: List[Dict] = []

    def detect(self) -> List[Dict]:
        """Run all detection methods."""
        self._detect_java()
        self._detect_python_pickle()
        self._detect_php()
        self._detect_json()
        self._detect_yaml()
        self._detect_xml()
        return self.results

    def _detect_java(self):
        """Detect Java serialization format."""
        if self.data.startswith(self.JAVA_MAGIC) or self.data.startswith(self.JAVA_MAGIC_ALT):
            version = self.data[3] if len(self.data) > 3 else 5
            self.results.append({
                'format': 'java',
                'confidence': 'high',
                'version': version,
                'description': f'Java Object Serialization Stream Protocol (version {version})',
                'magic_hex': self.data[:4].hex(),
                'magic_b64': base64.b64encode(self.data[:4]).decode() if len(self.data) >= 4 else None
            })

    def _detect_python_pickle(self):
        """Detect Python pickle format."""
        # Check raw pickle protocol markers
        for i, marker in enumerate(self.PICKLE_PROTOCOLS):
            if self.data.startswith(marker):
                self.results.append({
                    'format': 'python_pickle',
                    'confidence': 'high',
                    'protocol': i,
                    'description': f'Python pickle protocol {i}',
                    'magic_hex': marker.hex(),
                })
                return

        # Check base64 encoded pickle (protocol 4+)
        try:
            decoded = base64.b64decode(self.data.decode('utf-8', errors='ignore'))
            for i, marker in enumerate(self.PICKLE_PROTOCOLS):
                if decoded.startswith(marker):
                    self.results.append({
                        'format': 'python_pickle',
                        'confidence': 'high',
                        'protocol': i,
                        'description': f'Python pickle protocol {i} (base64 encoded)',
                        'encoding': 'base64'
                    })
                    return
        except:
            pass

        # Check for pickle-specific opcodes
        pickle_opcodes = {b'\x80', b'(', b'F', b'I', b'L', b'Y', b'N', b'T', b'}', b']'}
        if self.data[0:1] in pickle_opcodes or (len(self.data) > 1 and self.data[1:2] in pickle_opcodes):
            self.results.append({
                'format': 'python_pickle',
                'confidence': 'medium',
                'description': 'Possible Python pickle (legacy protocol)',
            })

    def _detect_php(self):
        """Detect PHP serialization format."""
        php_patterns = [
            (rb'^O:\d+:', 'PHP object'),
            (rb'^a:\d+:', 'PHP array'),
            (rb'^s:\d+:', 'PHP string'),
            (rb'^i:\d+;', 'PHP integer'),
            (rb'^b:[01];', 'PHP boolean'),
            (rb'^N;', 'PHP null'),
            (rb'^d:\d+\.\d+;', 'PHP float'),
        ]

        for pattern, desc in php_patterns:
            if re.match(pattern, self.data):
                self.results.append({
                    'format': 'php',
                    'confidence': 'high',
                    'description': f'PHP serialization ({desc})',
                    'pattern': pattern.decode()
                })
                return

    def _detect_json(self):
        """Detect JSON format."""
        try:
            import json
            text = self.data.decode('utf-8', errors='ignore').strip()
            if text.startswith('{') or text.startswith('['):
                json.loads(text)
                self.results.append({
                    'format': 'json',
                    'confidence': 'high',
                    'description': 'JSON format (deserialization vulnerability depends on parser)',
                    'note': 'Check for Jackson, Fastjson (Java) or jsonpickle (Python)'
                })
        except:
            pass

    def _detect_yaml(self):
        """Detect YAML format."""
        yaml_indicators = [b'!!python/', b'!!java.', b'---', b'%YAML']
        for indicator in yaml_indicators:
            if indicator in self.data:
                self.results.append({
                    'format': 'yaml',
                    'confidence': 'medium',
                    'description': 'YAML format (may contain deserialization tags)',
                    'indicator': indicator.decode()
                })
                return

    def _detect_xml(self):
        """Detect XML-based serialization."""
        xml_indicators = [b'<?xml', b'<java>', b'<object>', b'<bean>', b'<class>']
        for indicator in xml_indicators:
            if indicator in self.data:
                self.results.append({
                    'format': 'xml',
                    'confidence': 'medium',
                    'description': 'XML format (may contain deserialization)',
                    'indicator': indicator.decode()
                })
                return


def decode_input(input_str: str) -> bytes:
    """Try to decode input as base64, hex, or raw bytes."""
    # Try base64 first
    try:
        return base64.b64decode(input_str)
    except:
        pass

    # Try hex
    try:
        return binascii.unhexlify(input_str)
    except:
        pass

    # Try URL-safe base64
    try:
        return base64.urlsafe_b64decode(input_str)
    except:
        pass

    # Return as raw bytes
    return input_str.encode('utf-8', errors='ignore')


def format_output(results: List[Dict], verbose: bool = False) -> str:
    """Format detection results."""
    if not results:
        return "No serialization format detected.\n"

    lines = ["=== Serialization Format Detection ===\n"]

    for i, result in enumerate(results, 1):
        lines.append(f"\n[{i}] {result['format'].upper()}")
        lines.append(f"    Confidence: {result['confidence']}")
        lines.append(f"    Description: {result['description']}")

        if verbose:
            for key, value in result.items():
                if key not in ['format', 'confidence', 'description']:
                    lines.append(f"    {key}: {value}")

    lines.append("\n" + "="*40)
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='Detect serialization formats (Java, Python, PHP)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python3 detect_ser.py --input "rO0ABXNyABFqYXZhLnV0aWwuSGFzaE1hcAUH2s..."
    python3 detect_ser.py --input "gASVCgAAAAAAAACMBnN0cmluZ5Qu"
    python3 detect_ser.py --input "O:8:\"stdClass\":1:{...}"
    python3 detect_ser.py --file payload.bin --verbose
    echo "gASV..." | python3 detect_ser.py --stdin
        """
    )

    parser.add_argument('--input', '-i', help='Input string (base64, hex, or raw)')
    parser.add_argument('--file', '-f', help='Input file')
    parser.add_argument('--stdin', '-s', action='store_true', help='Read from stdin')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--json', action='store_true', help='Output as JSON')

    args = parser.parse_args()

    # Get input data
    if args.input:
        data = decode_input(args.input)
    elif args.file:
        with open(args.file, 'rb') as f:
            data = f.read()
    elif args.stdin:
        input_str = sys.stdin.read().strip()
        data = decode_input(input_str)
    else:
        parser.print_help()
        return 1

    # Detect format
    detector = SerializationDetector(data)
    results = detector.detect()

    # Output results
    if args.json:
        import json
        print(json.dumps(results, indent=2))
    else:
        print(format_output(results, args.verbose))

    return 0 if results else 1


if __name__ == '__main__':
    sys.exit(main())
