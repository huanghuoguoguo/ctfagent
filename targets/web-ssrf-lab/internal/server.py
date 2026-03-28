from flask import Flask

app = Flask(__name__)

@app.route('/flag')
@app.route('/')
def flag():
    # Flag hidden in internal service
    return "CTF{ssrf_successful_exploration_2026}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
