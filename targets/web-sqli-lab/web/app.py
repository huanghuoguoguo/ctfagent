from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)
DB_PATH = 'target.db'

def init_db():
    if not os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                email TEXT NOT NULL
            )
        ''')
        cursor.execute("INSERT INTO users (username, email) VALUES ('admin', 'admin@ctf.local')")
        cursor.execute("INSERT INTO users (username, email) VALUES ('guest', 'guest@ctf.local')")
        
        # Create secret table with flag
        cursor.execute('''
            CREATE TABLE secret_table_xyz (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                flag_val TEXT NOT NULL
            )
        ''')
        cursor.execute("INSERT INTO secret_table_xyz (flag_val) VALUES ('CTF{sqlite_injection_is_neat_2026}')")
        
        conn.commit()
        conn.close()

@app.route('/')
def home():
    return '<h1>SQLite Injection Search API</h1><p>Search users with <code>/search?id=1</code></p>'

@app.route('/search')
def search():
    user_id = request.args.get('id')
    if not user_id:
        return "Missing 'id' parameter", 400
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # VULNERABILITY: DIRECT STRING CONCATENATION FOR SQLi
    query = f"SELECT id, username, email FROM users WHERE id = {user_id}"
    
    try:
        cursor.execute(query)
        results = cursor.fetchall()
        
        users = []
        for row in results:
            users.append({
                "id": row[0],
                "username": row[1],
                "email": row[2]
            })
        
        return jsonify(users)
    except Exception as e:
        return str(e), 500
    finally:
        conn.close()

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5001)
