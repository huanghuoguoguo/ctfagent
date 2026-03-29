
from flask import Flask, request, jsonify
import pickle
import base64

app = Flask(__name__)

@app.route('/')
def home():
    return '<h1>Pickle Deserialization Lab</h1><p>Send base64-encoded pickle data via POST to <code>/process</code>.</p>'

@app.route('/process', methods=['POST'])
def process():
    data = request.json.get('data')
    if not data:
        return "No data provided. JSON field 'data' required.", 400
        
    try:
        # Vulnerability: Insecure deserialization
        raw_data = base64.b64decode(data)
        obj = pickle.loads(raw_data)
        return jsonify({"status": "data processed", "type": str(type(obj))})
    except Exception as e:
        return f"Deserialization error: {str(e)}", 500

if __name__ == '__main__':
    # Add flag file
    with open('/flag', 'w') as f:
        f.write("CTF{pickle_deserialization_is_dangerous}")
        
    app.run(host='0.0.0.0', port=5007)
