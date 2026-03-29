
from flask import Flask, request, render_template_string, make_response

app = Flask(__name__)

@app.route('/')
def home():
    return '<h1>XSS Lab</h1><ul><li><a href="/reflected?name=guest">Reflected XSS</a></li><li><a href="/dom">DOM-based XSS</a></li></ul>'

@app.route('/reflected')
def reflected():
    name = request.args.get('name', 'guest')
    # Vulnerability: Direct rendering of user input
    resp = make_response(render_template_string(f'<h1>Hello, {name}!</h1>'))
    resp.set_cookie('flag', 'CTF{reflected_xss_is_easy}')
    return resp

@app.route('/dom')
def dom():
    html = """
    <h1>DOM XSS Lab</h1>
    <div id="greeting"></div>
    <script>
        const name = decodeURIComponent(window.location.hash.substring(1)) || 'guest';
        // Vulnerability: innerHTML manipulation
        document.getElementById('greeting').innerHTML = `Hello, ${name}!`;
    </script>
    """
    resp = make_response(html)
    resp.set_cookie('secret', 'CTF{dom_xss_via_hash_sink}')
    return resp

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5006)
