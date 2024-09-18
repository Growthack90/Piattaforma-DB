from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from userModel import User, users

import sqlite3

app = Flask(__name__)


# Set Login
app.secret_key = 'your_secret_key'  # Sostituisci con una chiave segreta più sicura

# Configura Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(username):
    return User.get(username)


# STRUTTURA E CONNESSIONE DB
# Creazione e comunicazione con il database RdA (con aggiunta di una corretta gestione degli errori alle query del database per rilevare eccezioni e impedire l'arresto anomalo dell'applicazione)
def get_db_connection():
  try:
    connection = sqlite3.connect("database-rda.db")
    connection.row_factory = sqlite3.Row
    return connection
  except sqlite3.Error as e:
      print(f"Database connection error: {e}")
      return None  # Alternatively, raise a custom exception or handle it in the calling function.

# Creazione e comunicazione con il database fornitori (con aggiunta di una corretta gestione degli errori alle query del database per rilevare eccezioni e impedire l'arresto anomalo dell'applicazione)
def get_fornitori_db_connection():
  try:
    connection = sqlite3.connect("fornitori.db")
    connection.row_factory = sqlite3.Row
    return connection
  except sqlite3.Error as e:
    print(f"Fornitori database connection error: {e}")
  return None

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

# Home
@app.route('/')
@login_required
def home():
    return render_template('home.html', username=current_user.id)

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.get(username)
        if user and users[username]['password'] == password:
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid credentials, please try again.', 'danger')
    return render_template('login.html')

# Logout
@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# Index
@app.route('/index')
@login_required
def index():
    return render_template('index.html')

# Insert
@app.route('/insert', methods=['GET', 'POST'])
def insert():
    success = False
    try:
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

            connection = None
    
            if new_fornitore:
                fornitore = new_fornitore
                # Inserisci il nuovo fornitore nel database fornitori
                connection = get_fornitori_db_connection()
                if connection:
                    cursor = connection.cursor()
                    cursor.execute("INSERT OR IGNORE INTO fornitori (fornitore) VALUES (?)", (new_fornitore,))
                    connection.commit()
                    connection.close()
                else:
                    flash("Database connection error.", 'danger')
                    return render_template('insert.html', fornitori=[], success=False)

    
            # Inserisci i dati nel database RdA
            connection = get_db_connection()
            if connection:
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
        if connection:
            cursor = connection.cursor()
            cursor.execute("SELECT fornitore FROM fornitori")
            fornitori = [row['fornitore'] for row in cursor.fetchall()]
            connection.close()
        else:
            flash("Error retrieving suppliers.", 'danger')
            fornitori = []
    except sqlite3.Error as e:
        if connection:
            connection.rollback()
        print(f"Database error: {e}")
        flash("A database error occurred. Please try again.", 'danger')
        fornitori = []

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



# Logistics
@app.route('/logistics')
def logistics():
    return render_template('logistics.html')



# Modify
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
    if connection is None:
        return jsonify({"error": "Database connection error"}), 500
    
    try:
        cursor = connection.cursor()
    
        if doc_type == 'rda':
            cursor.execute("SELECT * FROM example WHERE rda = ?", (doc_value,))
        elif doc_type == 'ddt':
            cursor.execute("SELECT * FROM ddt WHERE id = ?", (doc_value,))
        else:
            return jsonify({"error": "Invalid document type"}), 400
    
        document = cursor.fetchone()
    
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return jsonify({"error": "Database query error"}), 500
    finally:
        connection.close()
    
        if document:
            return jsonify(dict(document)), 200
        else:
            return jsonify({"error": "Document not found"}), 404




# Modifica un documento
@app.route('/modify_document', methods=['POST'])
def modify_document():
    data = request.get_json()
    doc_id = data['id']
    updated_fields = data['updated_fields']

    connection = get_db_connection()
    if connection is None:
        return jsonify({"error": "Database connection error"}), 500

    try:
        cursor = connection.cursor()

        # Build the update query
        query = "UPDATE example SET "
        query += ", ".join([f"{key} = ?" for key in updated_fields.keys()])
        query += " WHERE id = ?"
        values = list(updated_fields.values()) + [doc_id]

        cursor.execute(query, values)
        connection.commit()
    except sqlite3.Error as e:
        connection.rollback()
        print(f"Error during update: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        connection.close()

    return jsonify({"success": True}), 200


# Assicurati che la tabella example nel tuo database SQLite abbia effettivamente le colonne che stai cercando di aggiornare. Puoi farlo eseguendo una query per visualizzare la struttura della tabella
@app.route('/check_table_structure')
def check_table_structure():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("PRAGMA table_info(example)")
    columns = cursor.fetchall()
    connection.close()
    return jsonify([dict(column) for column in columns]), 200

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

# Restituire elenco fornitori
@app.route('/get_fornitori', methods=['GET'])
def get_fornitori():
    connection = get_fornitori_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT fornitore FROM fornitori")
    fornitori = [row['fornitore'] for row in cursor.fetchall()]
    connection.close()
    return jsonify({"fornitori": fornitori})

# Search
@app.route('/search')
def search():
    return render_template('search.html')


# non dimenticare di cambiarlo in False prima di caricarlo sull'host per evitare qualsiasi attacco da parte di hacker
if __name__ == "__main__":
    app.run(debug=True)
