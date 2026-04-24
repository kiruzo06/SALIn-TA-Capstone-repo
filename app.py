from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app) # Allows the HTML file to talk to this server

def get_translation(text, src, tar):
    try:
        conn = sqlite3.connect('translations.db')
        cur = conn.cursor()
            
        # COLLATE NOCASE makes the search ignore Capital Letters
        query = "SELECT translated FROM translations WHERE source=? AND src_lang=? AND tar_lang=? COLLATE NOCASE"
        cur.execute(query, (text.strip().lower(), src, tar))
        
        result = cur.fetchone()
        conn.close()
        
        return result[0] if result else "No translation found"
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/')
def home():
    return "Salin-TA Backend is Running!"

@app.route('/translate', methods=['POST'])
def translate():
    data = request.json
    if not data or 'text' not in data:
        return jsonify({"translation": "Invalid Input"}), 400
        
    text = data['text']
    src = data['src']
    tar = data['tar']

    translated = get_translation(text, src, tar)
    return jsonify({"translation": translated})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
