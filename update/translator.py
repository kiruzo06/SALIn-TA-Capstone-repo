import sqlite3
import string
from difflib import SequenceMatcher

cache = {}

def clean_text(text):
    """
    Cleans the input text by converting to lowercase, 
    removing punctuation, and stripping extra whitespace.
    """
    text = text.lower().strip()
    # Remove punctuation using a translation table
    text = text.translate(str.maketrans('', '', string.punctuation))
    return text

def get_similarity(a, b):
    """Returns a float representing the similarity ratio between two strings."""
    return SequenceMatcher(None, a, b).ratio()

def word_based_score(a, b):
    a_words = a.split()
    b_words = b.split()
    matches = sum(1 for word in a_words if word in b_words)
    return matches / max(len(a_words), 1)

def translate(user_input, src_lang, tar_lang):
    """
    Searches the database for the best match and returns the translation.
    """
    conn = sqlite3.connect('translations.db')
    cursor = conn.cursor()

    key = (user_input, src_lang, tar_lang)

    if key in cache:
        return cache[key]
    
    # 1. Clean the user input
    cleaned_input = clean_text(user_input)
    
    # 2. Fetch all possible source phrases for the selected language pair
    # We filter by language first to narrow down the search space
    query = "SELECT source, translated FROM translations WHERE src_lang = ? AND tar_lang = ?"
    cursor.execute(query, (src_lang, tar_lang))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return None, "No data found for this language pair."

    # 3. Perform Fuzzy Matching
    # We will store results as (similarity_score, source_phrase, translated_phrase)
    matches = []
    
    for db_source, db_translated in rows:
        # Clean the DB source text for a fair comparison
        cleaned_db_source = clean_text(db_source)
        
        score = (
            get_similarity(cleaned_input, cleaned_db_source) * 0.6 +
            (1 if cleaned_input in cleaned_db_source else 0) * 0.4
        )
        
        matches.append({
            'score': score,
            'source': db_source,
            'translated': db_translated
        })

    # 4. Sort matches by score in descending order
    matches = sorted(matches, key=lambda x: x['score'], reverse=True)
    
    cache[key] = matches

    return matches

def detect_language(user_input):
    conn = sqlite3.connect('translations.db')
    cursor = conn.cursor()

    cleaned = clean_text(user_input)

    cursor.execute("SELECT src_lang, source FROM translations")
    rows = cursor.fetchall()
    conn.close()

    best_lang = None
    best_score = 0

    for lang, text in rows:
        score = get_similarity(cleaned, clean_text(text))
        if score > best_score:
            best_score = score
            best_lang = lang

    return best_lang

def main():
    print("--- Philippine Dialect Smart Translator ---")
    print("Available: English, Tagalog, Cebuano, Ilocano, Hiligaynon, Bicolano, Waray, Kapampangan, Pangasinan")
    
    while True:
        print("\n" + "="*40)
        user_text = input("Enter text to translate (or 'exit' to quit): ").strip()
        if user_text.lower() == 'exit':
            break
            
        src_lang = input("Source Language (e.g., English): ").strip().capitalize()
        tar_lang = input("Target Language (e.g., Tagalog): ").strip().capitalize()

        if src_lang == "":
            src_lang = detect_language(user_text)
            print(f"Auto-detected source language: {src_lang}")

        results = translate(user_text, src_lang, tar_lang)

        if isinstance(results, str): # Error message
            print(f"Error: {results}")
            continue

        if not results:
            print("No translations found in the database.")
            continue


        # Get the best match
        best_match = results[0]

        # Threshold check: if similarity is too low, warn the user
        if best_match['score'] == 1.0:
            print(f"\nExact match found!")
            print(f"Result: {best_match['translated']}")
        elif best_match['score'] > 0.6:
            print(f"\nClosest match found ({round(best_match['score'] * 100, 1)}% confidence):")
            print(f"Original word in DB: '{best_match['source']}'")
            print(f"Translation: {best_match['translated']}")
            
            # Show top 3 alternatives if they exist and are relevant
            if len(results) > 1 and results[1]['score'] > 0.3:
                print("\nOther possible matches:")
                for alt in results[1:3]:
                    print(f"- {alt['source']} -> {alt['translated']} ({round(alt['score']*100)}%)")
        else:
            print("\nNo confident match found. Maybe try a different word?")

if __name__ == "__main__":
    # Ensure the database exists before running
    try:
        main()
    except sqlite3.OperationalError:
        print("Database error: Make sure 'translations.db' exists and is initialized.")
