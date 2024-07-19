import sqlite3

def init_fornitori_db():
    connection = sqlite3.connect("fornitori.db")
    cursor = connection.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fornitori (
        id INTEGER PRIMARY KEY,
        fornitore TEXT NOT NULL
    )
    """)
    connection.commit()
    
    # Inserisci tre fornitori
    fornitori = [
        ("Fornitore A",),
        ("Fornitore B",),
        ("Fornitore C",)
    ]
    
    cursor.executemany("INSERT INTO fornitori (fornitore) VALUES (?)", fornitori)
    connection.commit()
    connection.close()

init_fornitori_db()
print("Database fornitori.db popolato con successo.")