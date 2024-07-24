from flask import Flask, render_template, request, jsonify
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
    # Tabella dei fornitori (file 'fornitori.db')
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

    # Tabella example (file 'database.db')
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS example (
        id INTEGER PRIMARY KEY,
        rda INTEGER NOT NULL,
        basket_name TEXT NOT NULL,
        fornitore TEXT NOT NULL,
        importo_sc INTEGER NOT NULL,
        oda INTEGER NOT NULL,
        commessa TEXT NOT NULL,
        element TEXT NOT NULL,
        richiedente TEXT NOT NULL,
        data_creazione TEXT NOT NULL,
        tipologia_acquisto TEXT NOT NULL
    )
    """)

    # # Tabella ddt (se esiste)
    # cursor.execute("""
    # CREATE TABLE IF NOT EXISTS ddt (
    #     id INTEGER PRIMARY KEY,
    #     field1 TEXT NOT NULL,
    #     field2 TEXT NOT NULL
    #     -- Aggiungi altri campi secondo le tue necessità
    # )
    # """)

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

#########################################################################################
# INSERT
#########################################################################################

@app.route('/insert', methods=['GET', 'POST'])
def insert():
    success = False
    if request.method == 'POST':
        rda = request.form['rda']
        basket_name = request.form['basket_name']
        fornitore = request.form['fornitore']
        new_fornitore = request.form['new_fornitore']
        importo_sc = request.form['importo_sc']
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
            INSERT INTO example (rda, basket_name, fornitore, importo_sc, oda, commessa, element, richiedente, data_creazione, tipologia_acquisto)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (rda, basket_name, fornitore, importo_sc, oda, commessa, element, richiedente, data_creazione, tipologia_acquisto))
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

# Show rdas
@app.route('/show_rdas')
def show_rdas():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM example")
    rdas = cursor.fetchall()
    connection.close()
    return render_template('rdas.html', rdas=rdas)

# Add fornitori
@app.route('/add_fornitore', methods=['POST'])
def add_fornitore():
    data = request.get_json()
    new_fornitore = data.get('fornitore')

    if new_fornitore:
        connection = get_fornitori_db_connection()
        cursor = connection.cursor()
        cursor.execute("INSERT OR IGNORE INTO fornitori (fornitore) VALUES (?)", (new_fornitore,))
        connection.commit()
        connection.close()

        return {"success": True}
    return {"success": False}, 400

# Show fornitori
@app.route('/show_fornitori')
def show_fornitori():
    connection = get_fornitori_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM fornitori")
    fornitori = cursor.fetchall()
    connection.close()
    return render_template('fornitori.html', fornitori=fornitori)

#########################################################################################
# LOGISTICS
#########################################################################################

@app.route('/logistics')
def logistics():
    return render_template('logistics.html')

#########################################################################################
# MODIFY
#########################################################################################

@app.route('/modify')
def modify():
    return render_template('modify.html')

# Cerca un documento per ID
@app.route('/search_document', methods=['POST'])
def search_document():
    data = request.get_json()
    doc_type = data['doc_type']
    doc_value = data['doc_value']

    connection = get_db_connection()
    cursor = connection.cursor()

    if doc_type == 'rda':
        cursor.execute("SELECT * FROM example WHERE rda = ?", (doc_value,))
    elif doc_type == 'ddt':
        cursor.execute("SELECT * FROM ddt WHERE id = ?", (doc_value,))
    else:
        connection.close()
        return jsonify({"error": "Tipo di documento non valido"}), 400

    document = cursor.fetchone()
    connection.close()

    if document:
        return jsonify(dict(document)), 200
    else:
        return jsonify({"error": "Documento non trovato"}), 404

# Modifica un documento
@app.route('/modify_document', methods=['POST'])
def modify_document():
    data = request.get_json()
    doc_id = data['id']
    updated_fields = data['updated_fields']

    connection = get_db_connection()
    cursor = connection.cursor()

    query = "UPDATE example SET "
    query += ", ".join([f"{key} = ?" for key in updated_fields.keys()])
    query += " WHERE id = ?"
    values = list(updated_fields.values()) + [doc_id]

    try:
        cursor.execute(query, values)
        connection.commit()
        return jsonify({"success": True}), 200
    except Exception as e:
        connection.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        connection.close()

    return jsonify({"success": True}), 200

# Elimina un documento
@app.route('/delete_document', methods=['POST'])
def delete_document():
    data = request.get_json()
    doc_id = data['id']

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("DELETE FROM example WHERE id = ?", (doc_id,))
        connection.commit()
        return jsonify({"success": True}), 200
    except Exception as e:
        connection.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        connection.close()

    return jsonify({"success": True}), 200

#########################################################################################
# SEARCH
#########################################################################################

@app.route('/search')
def search():
    return render_template('search.html')


if __name__ == "__main__":
    app.run(debug=True)
