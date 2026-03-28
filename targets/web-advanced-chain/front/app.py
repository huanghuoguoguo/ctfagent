from flask import Flask, request, abort
import requests
import socket
from urllib.parse import urlparse

app = Flask(__name__)

def is_blacklisted(url):
    parsed = urlparse(url)
    hostname = parsed.hostname
    if not hostname:
        return True
    
    # 1. Direct block of common strings
    blacklist_strings = ['localhost', '127.0.0.1', '127.1', '2130706433']
    for s in blacklist_strings:
        if s in hostname:
            return True
            
    # 2. Block direct IP to 127.0.0.1
    try:
        ip = socket.gethostbyname(hostname)
        if ip.startswith('127.'):
            return True
    except:
        pass
        
    return False

@app.route('/')
def home():
    return '<h1>SSRF Proxy Hardened</h1><p>Usage: <code>/proxy?url=http://example.com</code></p><p>Note: No internal access allowed.</p>'

@app.route('/proxy')
def proxy():
    url = request.args.get('url')
    if not url:
        return "Missing URL", 400
        
    if is_blacklisted(url):
        return "Access to internal resource is strictly prohibited!", 403
        
    try:
        # Simple fetcher
        r = requests.get(url, timeout=3)
        return r.text
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)
