from flask import Flask, request, render_template_string
import os
import subprocess

app = Flask(__name__)

INDEX_TEMPLATE = '''
<h1>Network Tool</h1>
<p>Check if a host is up:</p>
<form method="GET" action="/ping">
    <input type="text" name="host" placeholder="8.8.8.8">
    <input type="submit" value="Ping">
</form>
'''

@app.route('/')
def home():
    return render_template_string(INDEX_TEMPLATE)

@app.route('/ping')
def ping():
    host = request.args.get('host')
    if not host:
        return "Host parameter is missing.", 400
    
    # VULNERABILITY: COMMAND INJECTION
    try:
        # User input is directly passed to shell=True
        command = f"ping -c 1 {host}"
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        return f"<pre>{output.decode()}</pre>"
    except subprocess.CalledProcessError as e:
        return f"<pre>Error: {e.output.decode()}</pre>", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
