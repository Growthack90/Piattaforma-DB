from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

# Creazione e comunicazione con il database RdA
def get_db_connection():
    connection = sqlite3.connect("database-rda.db")
    connection.row_factory = sqlite3.Row
    return connection

# Creazione e comunicazione con il database fornitori
def get_fornitori_db_connection():
    connection = sqlite3.connect("fornitori.db")
    connection.row_factory = sqlite3.Row
    return connection

# Crea la struttura dei database se non esiste
def init_fornitori_db():
    connection = get_fornitori_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fornitori (
        fornitore TEXT PRIMARY KEY
    )
    """)
    connection.commit()
    connection.close()

def init_db():
    # Database RdA
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS example (
        id INTEGER PRIMARY KEY,
        rda INTEGER NOT NULL,
        basket_name TEXT NOT NULL,
        fornitore TEXT NOT NULL,
        valore_shopping_cart INTEGER NOT NULL,
        oda INTEGER NOT NULL,
        commessa TEXT NOT NULL,
        element TEXT NOT NULL,
        richiedente TEXT NOT NULL,
        data_creazione TEXT NOT NULL,
        tipologia_acquisto TEXT NOT NULL
    )
    """)
    connection.commit()
    connection.close()

    # Database Fornitori
    init_fornitori_db()

init_db()

# # Controllare se il database è stato creato con successo. Se non presente alcun dato nel database il valore di ritorno è "0"
# print(connection.total_changes)

# INDEX
@app.route('/')
def index():
    return render_template('index.html')

# INSERT
@app.route('/insert', methods=['GET', 'POST'])
def insert():
    success = False
    if request.method == 'POST':
        rda = request.form['rda']
        basket_name = request.form['basket_name']
        fornitore = request.form['fornitore']
        new_fornitore = request.form['new_fornitore']
        valore_shopping_cart = request.form['valore_shopping_cart']
        oda = request.form['oda']
        commessa = request.form['commessa']
        element = request.form['element']
        richiedente = request.form['richiedente']
        data_creazione = request.form['data_creazione']
        tipologia_acquisto = request.form['tipologia_acquisto']

        if new_fornitore:
            fornitore = new_fornitore
            # Inserisci il nuovo fornitore nel database fornitori
            connection = get_fornitori_db_connection()
            cursor = connection.cursor()
            cursor.execute("INSERT OR IGNORE INTO fornitori (fornitore) VALUES (?)", (new_fornitore,))
            connection.commit()
            connection.close()

        # Inserisci i dati nel database RdA
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO example (rda, basket_name, fornitore, valore_shopping_cart, oda, commessa, element, richiedente, data_creazione, tipologia_acquisto)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (rda, basket_name, fornitore, valore_shopping_cart, oda, commessa, element, richiedente, data_creazione, tipologia_acquisto))
        connection.commit()
        connection.close()

        success = True

    # Recupera l'elenco dei fornitori dal database fornitori.db
    connection = get_fornitori_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT fornitore FROM fornitori")
    fornitori = [row['fornitore'] for row in cursor.fetchall()]
    connection.close()

    return render_template('insert.html', fornitori=fornitori, success=success)


# SHOW RDAs
@app.route('/show_rdas')
def show_rdas():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM example")
    rdas = cursor.fetchall()
    connection.close()
    return render_template('rdas.html', rdas=rdas)

# LOGISTICS
@app.route('/logistics')
def logistics():
    return render_template('logistics.html')

# MODIFY
@app.route('/modify')
def modify():
    return render_template('modify.html')

# SEARCH
@app.route('/search')
def search():
    return render_template('search.html')

if __name__ == "__main__":
    app.run(debug=True)
