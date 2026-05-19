import sqlite3
from flask import Flask, jsonify, request
from flask_cors import CORS
from translator import translate, smart_translate, DB_PATH

app = Flask(__name__)
CORS(app)

# --- ROUTER FOR DASHBOARD TRANSLATION ---
@app.route('/translate', methods=['POST'])
def handle_translate():
    data = request.json
    user_text = data.get('text', '').strip()
    src_lang = data.get('src', '').capitalize()
    tar_lang = data.get('tar', '').capitalize()

    if not user_text:
        return jsonify({"translation": ""})

    # Call the new Smart Hybrid logic
    result = smart_translate(user_text, src_lang, tar_lang)

    return jsonify({"translation": result})

# --- ROUTE FOR IDIOMS & SLANGS ---
@app.route('/idioms', methods=['GET'])
def get_idioms():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row

        # Fetch idioms
        idioms = conn.execute('SELECT phrase, meaning, english_equivalent FROM idioms').fetchall()
        idioms_list = [dict(row) for row in idioms]
        for item in idioms_list:
            item['english'] = item.pop('english_equivalent')
            item['type'] = 'idiom'

        # Fetch slangs
        try:
            slangs = conn.execute('SELECT phrase, meaning, english_equivalent FROM slangs').fetchall()
            slangs_list = [dict(row) for row in slangs]
            for item in slangs_list:
                item['english'] = item.pop('english_equivalent')
                item['type'] = 'slang'
        except:
            slangs_list = []

        conn.close()
        return jsonify(idioms_list + slangs_list)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- ROUTE FOR COMMON PHRASES ---
@app.route('/phrases', methods=['GET'])
def get_phrases():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        rows = conn.execute('''
            SELECT english, tagalog, bisaya, ilocano,
                   hiligaynon, bicolano, waray, kapampangan, pangasinan
            FROM common_phrases
        ''').fetchall()
        conn.close()
        return jsonify([dict(row) for row in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- ROUTE TO CHECK IF WORD IS SLANG OR IDIOM ---
@app.route('/check-special', methods=['POST'])
def check_special():
    try:
        data = request.json
        word = data.get('word', '').strip().lower()

        conn = sqlite3.connect(DB_PATH)

        # Check slang
        is_slang = conn.execute(
            'SELECT 1 FROM slangs WHERE LOWER(phrase) = ?', (word,)
        ).fetchone() is not None

        # Check idiom
        is_idiom = conn.execute(
            'SELECT 1 FROM idioms WHERE LOWER(phrase) = ?', (word,)
        ).fetchone() is not None

        conn.close()
        return jsonify({"is_slang": is_slang, "is_idiom": is_idiom})
    except:
        return jsonify({"is_slang": False, "is_idiom": False})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
