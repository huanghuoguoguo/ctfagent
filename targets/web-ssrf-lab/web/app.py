from flask import Flask, request
import requests

app = Flask(__name__)

@app.route('/')
def home():
    return '<h1>SSRF Lab Vulnerable Front-end</h1><p>Try the <code>/proxy?url=http://example.com</code> endpoint.</p>'

@app.route('/proxy')
def proxy():
    url = request.args.get('url')
    if not url:
        return "Usage: /proxy?url=http://example.com", 400
    try:
        # SSRF Vulnerability: No filtering on URL
        response = requests.get(url, timeout=5)
        return response.text
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
