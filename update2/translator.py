import sqlite3
import string
import os
import re
from difflib import SequenceMatcher

# --- ANDROID PATH FIX ---
basedir = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(basedir, 'translations.db')

cache = {}

def clean_text(text):
    if not text:
        return ""
    text = text.lower().strip()
    text = text.replace('-', ' ')
    text = text.translate(str.maketrans('', '', string.punctuation))
    return text

def get_similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

def contains_whole_word(word, text):
    if ' ' in word:
        return word in text
    return bool(re.search(r'\b' + re.escape(word) + r'\b', text))

def translate(user_input, src_lang, tar_lang):
    """
    Standard fuzzy search for the whole phrase in the database.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
    except sqlite3.OperationalError:
        return "Database Error"

    key = (user_input, src_lang, tar_lang)
    if key in cache:
        return cache[key]
    
    cleaned_input = clean_text(user_input)
    
    query = "SELECT source, translated FROM translations WHERE src_lang = ? AND tar_lang = ?"
    cursor.execute(query, (src_lang, tar_lang))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return []

    matches = []
    for db_source, db_translated in rows:
        cleaned_db_source = clean_text(db_source)
        score = (get_similarity(cleaned_input, cleaned_db_source) * 0.6 +
                (1 if contains_whole_word(cleaned_input, cleaned_db_source) else 0) * 0.4)

        
        matches.append({
            'score': score,
            'source': db_source,
            'translated': db_translated
        })

    matches = sorted(matches, key=lambda x: x['score'], reverse=True)
    cache[key] = matches
    return matches

def apply_case_style(original_input, translated_text):
    if not translated_text:
        return translated_text

    stripped = original_input.strip()

    if stripped.isupper():
        return translated_text.upper()
    elif stripped.islower():
        return translated_text.lower()
    elif stripped.istitle():
        return translated_text.title()
    else:
        return translated_text[0].upper() + translated_text[1:] if translated_text else translated_text


def smart_translate(user_input, src_lang, tar_lang):
    if not user_input.strip():
        return ""

    original_input = user_input  # save original casing

    # 0. Normalize no-space input (e.g. "goodmorning" → "good morning")
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT source FROM translations WHERE src_lang = ? AND tar_lang = ?", (src_lang, tar_lang))
        all_sources = [row[0] for row in cursor.fetchall()]
        conn.close()

        cleaned_no_space = user_input.lower().replace(" ", "")
        for source in all_sources:
            if source.lower().replace(" ", "") == cleaned_no_space:
                user_input = source  # swap to DB version with proper spacing
                break
    except:
        pass

    # 1. Try full sentence match first
    full_matches = translate(user_input, src_lang, tar_lang)
    if not isinstance(full_matches, str) and full_matches and full_matches[0]['score'] > 0.85:
        return apply_case_style(original_input, full_matches[0]['translated'])

    # 2. Break into words for hybrid translation
    words = user_input.split()
    translated_parts = []
    i = 0

    while i < len(words):
        match_found = False

        for length in range(min(4, len(words) - i), 0, -1):
            chunk = " ".join(words[i : i + length])
            matches = translate(chunk, src_lang, tar_lang)

            threshold = 0.8 if length > 1 else 0.7

            if not isinstance(matches, str) and matches and matches[0]['score'] >= threshold:
                translated_parts.append(matches[0]['translated'])
                i += length
                match_found = True
                break

        if not match_found:
            translated_parts.append(words[i])
            i += 1

    result = " ".join(translated_parts)
    return apply_case_style(original_input, result)


    """
    Advanced logic that breaks sentence into pieces and translates known parts,
    leaving names and unknown words as-is.
    """
    if not user_input.strip():
        return ""

    # 1. Try full sentence match first (if it's very confident)
    full_matches = translate(user_input, src_lang, tar_lang)
    if not isinstance(full_matches, str) and full_matches and full_matches[0]['score'] > 0.85:
        return full_matches[0]['translated']

    # 2. Break into words for hybrid translation
    words = user_input.split()
    translated_parts = []
    i = 0

    while i < len(words):
        match_found = False

        # Try matching phrases (up to 4 words long)
        for length in range(min(4, len(words) - i), 0, -1):
            chunk = " ".join(words[i : i + length])
            matches = translate(chunk, src_lang, tar_lang)

            # Confidence threshold: 0.8 for phrases, 0.7 for single words
            threshold = 0.8 if length > 1 else 0.7

            if not isinstance(matches, str) and matches and matches[0]['score'] >= threshold:
                translated_parts.append(matches[0]['translated'])
                i += length
                match_found = True
                break

        if not match_found:
            # Keep original word if no translation found (e.g. Names like "Paul")
            translated_parts.append(words[i])
            i += 1

    return " ".join(translated_parts)

def detect_language(user_input):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
    except:
        return None
    cleaned = clean_text(user_input)
    cursor.execute("SELECT src_lang, source FROM translations")
    rows = cursor.fetchall()
    conn.close()
    best_lang, best_score = None, 0
    for lang, text in rows:
        score = get_similarity(cleaned, clean_text(text))
        if score > best_score:
            best_score, best_lang = score, lang
    return best_lang
