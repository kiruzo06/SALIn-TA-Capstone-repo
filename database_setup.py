import sqlite3
import itertools

def init_db():
    conn = sqlite3.connect('translations.db')
    cur = conn.cursor()
    
    cur.execute("DROP TABLE IF EXISTS translations")
    cur.execute("""
    CREATE TABLE translations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source TEXT,
        translated TEXT,
        src_lang TEXT,
        tar_lang TEXT
    )
    """)

    languages = [
        "English", "Tagalog", "Cebuano", "Ilocano", 
        "Hiligaynon", "Bicolano", "Waray", "Kapampangan", "Pangasinan"
    ]

    # CATEGORIZED COMMON CONCEPTS
    concepts = [
        # --- GREETINGS & ETIQUETTE ---
        {
            "English": "Hello", "Tagalog": "Kumusta", "Cebuano": "Kumusta", "Ilocano": "Kablaaw", 
            "Hiligaynon": "Kamusta", "Bicolano": "Kumusta", "Waray": "Kumusta", "Kapampangan": "Komusta", "Pangasinan": "Kumusta"
        },
        {
            "English": "Good morning", "Tagalog": "Magandang umaga", "Cebuano": "Maayong buntag", "Ilocano": "Naimbag a bigat", 
            "Hiligaynon": "Maayong aga", "Bicolano": "Marhay na aga", "Waray": "Maupay nga aga", "Kapampangan": "Mayap a abak", "Pangasinan": "Maabig a kabuasan"
        },
        {
            "English": "Good evening", "Tagalog": "Magandang gabi", "Cebuano": "Maayong gabi-i", "Ilocano": "Naimbag a gabi", 
            "Hiligaynon": "Maayong gab-i", "Bicolano": "Marhay na banggi", "Waray": "Maupay nga gabi", "Kapampangan": "Mayap a bengi", "Pangasinan": "Maabig a labi"
        },
        {
            "English": "Thank you", "Tagalog": "Salamat", "Cebuano": "Salamat", "Ilocano": "Agyamanak", 
            "Hiligaynon": "Salamat", "Bicolano": "Salamat", "Waray": "Salamat", "Kapampangan": "Salamat", "Pangasinan": "Salamat"
        },
        {
            "English": "Yes", "Tagalog": "Oo", "Cebuano": "Oo", "Ilocano": "Wen", 
            "Hiligaynon": "Huo", "Bicolano": "Iyo", "Waray": "Oo", "Kapampangan": "Wa", "Pangasinan": "On"
        },
        {
            "English": "No", "Tagalog": "Hindi", "Cebuano": "Dili", "Ilocano": "Saan", 
            "Hiligaynon": "Indi", "Bicolano": "Dai", "Waray": "Dire", "Kapampangan": "Ali", "Pangasinan": "Andi"
        },

        # --- COMMON QUESTIONS ---
        {
            "English": "What is your name?", "Tagalog": "Ano ang pangalan mo?", "Cebuano": "Unsay ngalan nimo?", "Ilocano": "Ania ti naganmo?", 
            "Hiligaynon": "Ano ang ngalan mo?", "Bicolano": "Ano an saimong pangaran?", "Waray": "Ano it imo ngaran?", "Kapampangan": "Nanung lagyu mu?", "Pangasinan": "Antoy ngaran mo?"
        },
        {
            "English": "How much?", "Tagalog": "Magkano?", "Cebuano": "Tagpila?", "Ilocano": "Mano?", 
            "Hiligaynon": "Tagpila?", "Bicolano": "Gurano?", "Waray": "Tagpira?", "Kapampangan": "Magkanu?", "Pangasinan": "Pigatyo?"
        },
        {
            "English": "Where is the toilet?", "Tagalog": "Nasaan ang banyo?", "Cebuano": "Asa ang banyo?", "Ilocano": "Ayanna ti banyo?", 
            "Hiligaynon": "Diin ang banyo?", "Bicolano": "Hain an banyo?", "Waray": "Hain an banyo?", "Kapampangan": "Nukarin ing banyu?", "Pangasinan": "Iner so banyo?"
        },

        # --- SURVIVAL PHRASES ---
        {
            "English": "I don't know", "Tagalog": "Hindi ko alam", "Cebuano": "Wala ko kabalo", "Ilocano": "Diak ammo", 
            "Hiligaynon": "Wala ko kabalo", "Bicolano": "Dai ko aram", "Waray": "Dire ko maaram", "Kapampangan": "Eku balu", "Pangasinan": "Agko amta"
        },
        {
            "English": "Help", "Tagalog": "Saklolo", "Cebuano": "Tabang", "Ilocano": "Tulong", 
            "Hiligaynon": "Tabang", "Bicolano": "Tabang", "Waray": "Tabang", "Kapampangan": "Saup", "Pangasinan": "Tulong"
        },
        {
            "English": "Take care", "Tagalog": "Ingat", "Cebuano": "Amping", "Ilocano": "Alwad", 
            "Hiligaynon": "Halong", "Bicolano": "Kugos", "Waray": "Pag-amping", "Kapampangan": "Mimingat", "Pangasinan": "Alwar"
        },

        # --- BASIC VERBS (Infinitive/Present) ---
        {
            "English": "Eat", "Tagalog": "Kain", "Cebuano": "Kaon", "Ilocano": "Mangan", 
            "Hiligaynon": "Kaon", "Bicolano": "Kakan", "Waray": "Kaon", "Kapampangan": "Mangan", "Pangasinan": "Pangan"
        },
        {
            "English": "Sleep", "Tagalog": "Tulog", "Cebuano": "Tulog", "Ilocano": "Maturog", 
            "Hiligaynon": "Tulog", "Bicolano": "Turog", "Waray": "Katurog", "Kapampangan": "Matudtud", "Pangasinan": "Ukol"
        },
        {
            "English": "Drink", "Tagalog": "Inom", "Cebuano": "Inom", "Ilocano": "Uminum", 
            "Hiligaynon": "Inom", "Bicolano": "Inom", "Waray": "Inom", "Kapampangan": "Minum", "Pangasinan": "Inum"
        }
    ]

    final_data = []
    for concept in concepts:
        pairs = list(itertools.permutations(languages, 2))
        for src, tar in pairs:
            if src in concept and tar in concept:
                final_data.append((
                    concept[src].lower(), 
                    concept[tar],         
                    src,                  
                    tar                   
                ))

    cur.executemany(
        "INSERT INTO translations (source, translated, src_lang, tar_lang) VALUES (?, ?, ?, ?)", 
        final_data
    )

    conn.commit()
    conn.close()
    print(f"✅ Database Rebuilt with {len(final_data)} pairs across 9 dialects!")

if __name__ == '__main__':
    init_db()
