from flask import Flask, request, jsonify
from flask_cors import CORS
from translator import translate
import sqlite3

app = Flask(__name__)
CORS(app) # Allows the HTML file to talk to this server

@app.route('/translate', methods=['POST'])
def translate_route():
    data = request.json

    if not data or 'text' not in data:
        return jsonify({"translation": "Invalid Input"}), 400

    text = data['text']
    src = data['src']
    tar = data['tar']

    results = translate(text, src, tar)

    if isinstance(results, str):
        return jsonify({"translation": results})

    best = results[0]['translated'] if results else "No translation found"

    return jsonify({"translation": best})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
