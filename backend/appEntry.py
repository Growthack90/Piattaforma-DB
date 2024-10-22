from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from userModel import User, users
import sqlite3
# import os

app = Flask(__name__, template_folder='../frontend/templates') # Flask, per impostazione predefinita, cerca i template nella cartella templates situata nella stessa directory del file app.py.  Per indicare a Flask dove trovare i template in una struttura di directory personalizzata, devi configurare la variabile template_folder durante l'inizializzazione dell'app

app.config.from_object('config')

# Configura Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(username):
    return User.get(username)


# CONNESSIONE DB RDA
# Creazione e comunicazione con il database RdA (con aggiunta di una corretta gestione degli errori alle query del database per rilevare eccezioni e impedire l'arresto anomalo dell'applicazione)
def get_db_connection():
  try:
    connection = sqlite3.connect("database-rda.db")
    connection.row_factory = sqlite3.Row
    return connection
  except sqlite3.Error as e:
      print(f"Database connection error: {e}")
      return None  # Alternatively, raise a custom exception or handle it in the calling function.


# CONNESSIONE DB FORNITORI
# Creazione e comunicazione con il database fornitori (con aggiunta di una corretta gestione degli errori alle query del database per rilevare eccezioni e impedire l'arresto anomalo dell'applicazione)
def get_fornitori_db_connection():
  try:
    connection = sqlite3.connect("fornitori.db")
    connection.row_factory = sqlite3.Row
    return connection
  except sqlite3.Error as e:
    print(f"Fornitori database connection error: {e}")
  return None


# CONNESSIONE DB DDT
def get_ddt_db_connection():
    try:
        connection = sqlite3.connect("ddt.db")
        connection.row_factory = sqlite3.Row
        return connection
    except sqlite3.Error as e:
        print(f"DDT database connection error: {e}")
        return None


# INIZIALIZZAZIONE STRUTTURA DB FORNITORI
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


# INIZIALIZZAZIONE STRUTTURA DB RDA
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
    connection.commit()
    connection.close()


# INIZIALIZZAZIONE DB DDT
def init_ddt_db():
    connection = get_ddt_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ddt (
        id INTEGER PRIMARY KEY,
        costo_unitario TEXT NOT NULL,
        quantita TEXT NOT NULL,
        ubicazione TEXT NOT NULL,
        descrizione TEXT NOT NULL,
        ddt TEXT NOT NULL,
        data_ordine TEXT NOT NULL,
        fornitore TEXT NOT NULL,
        arrivato TEXT NOT NULL,
        data_arrivo_ordine TEXT NOT NULL
    )
    """)
    connection.commit()
    connection.close()



# Database Fornitori
init_fornitori_db()

# Database RdA
init_db()

# Database DDT
init_ddt_db()

# # Controllare se il database è stato creato con successo. Se non presente alcun dato nel database il valore di ritorno è "0"
# print(connection.total_changes)


############################################################################################################
# CREAZIONE ENDPOINT
############################################################################################################

# Home
@app.route('/')
@login_required # verifica se l'utente è loggato. Se non lo è, reindirizza l'utente alla pagina di login
def home():
    return render_template('home.html', username=current_user.id)
##########################################################

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            username = request.form['username']
            password = request.form['password']
            user = User.get(username)
            if user and users[username]['password'] == password:
                login_user(user)
                flash('Login successful!', 'success')
                return redirect(url_for('home'))
            else:
                flash('Invalid credentials, please try again.', 'danger')
        except Exception as e:  # Cattura qualsiasi tipo di eccezione
            print(f"Errore durante il login: {e}")  # Stampa l'errore nella console per il debugging
            flash("Si è verificato un errore durante il login. Riprova.", "danger")

    return render_template('login.html')
##########################################################

# Logout
@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))
##########################################################

# Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if User.create(username, password):
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Username already exists. Please choose a different one.', 'danger')

    return render_template('register.html') 
##########################################################

# Index
@app.route('/index')
@login_required
def index():
    return render_template('index.html')
##########################################################

# Insert RdA
@app.route('/insert_rdas', methods=['GET', 'POST'])
@login_required
def insert_rda():
    success = False
    fornitori = []  # Inizializza la lista dei fornitori
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

            # Aggiungi nuovo fornitore   
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
                    return render_template('insert_rda.html', fornitori=[], success=False)

    
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

    return render_template('insert_rda.html', fornitori=fornitori, success=success)
##########################################################


# Insert DDT
@app.route('/insert_ddts', methods=['GET', 'POST'])
@login_required
def insert_ddt():
    success = False  # Inizializza il flag di successo a False
    fornitori = []  # Inizializza la lista dei fornitori
    try:
        if request.method == 'POST':
            costo_unitario = request.form['costo_unitario']
            quantita = request.form['quantita']
            ubicazione = request.form['ubicazione']
            descrizione = request.form['descrizione']
            ddt = request.form['ddt']
            data_ordine = request.form['data_ordine']
            fornitore = request.form['fornitore']
            new_fornitore = request.form['new_fornitore']
            arrivato = request.form['arrivato']
            data_arrivo_ordine = request.form['data_arrivo_ordine']
            connection = None
            # Aggiungi nuovo fornitore   
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
                    return render_template('insert_ddt.html', fornitori=[], success=False)
            # Inserisci i dati nel database DDT
            connection = get_ddt_db_connection()
            if connection:
                cursor = connection.cursor()
                cursor.execute("""
                    INSERT INTO ddt (costo_unitario, quantita, ubicazione, descrizione, ddt, data_ordine, fornitore, arrivato, data_arrivo_ordine) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (costo_unitario, quantita, ubicazione, descrizione, ddt, data_ordine, fornitore, arrivato, data_arrivo_ordine))
                connection.commit()
                success = True  # Imposta il flag di successo a True se l'inserimento ha avuto successo

                # Recupera l'elenco dei fornitori dal database fornitori.db
                connection = get_fornitori_db_connection()
                if connection:
                    cursor = connection.cursor()
                    cursor.execute("SELECT fornitore FROM fornitori")
                    fornitori = [row['fornitore'] for row in cursor.fetchall()]
                    connection.close()  # Chiudi la connessione DOPO aver recuperato i fornitori
                else:
                    flash("Error retrieving suppliers.", 'danger')
                    # fornitori is already initialized to an empty list                    
    except sqlite3.Error as e:
        if connection:
            connection.rollback()
        print(f"Database error: {e}")
        flash("A database error occurred. Please try again.", 'danger')
        # fornitori is already initialized to an empty list 

    return render_template('insert_ddt.html', fornitori=fornitori, success=success)
##########################################################


# Show ddts
@app.route('/show_ddts')
@login_required
def show_ddts():
    connection = get_ddt_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM ddt")
    ddts = cursor.fetchall()

    # debug --> stampa il valore di ddts e verificare che contenga i dati recuperati dal database
    print(ddts)  # Stampa la lista di tuple recuperata dal database. Ogni tupla rappresenta una riga della tabella ddt.
    print(type(ddts))  # Stampa il tipo di dato di ddts (dovrebbe essere <class 'list'>)

    # Il ciclo for itera sulla lista ddts e stampa ogni singola tupla, rendendo l'output più leggibile.
    for ddt in ddts:
        print(ddt)  # Stampa ogni tupla nella lista
        print(ddt['id'])           # Stampa il valore della colonna 'id'
        print(ddt['costo_unitario'])
        print(ddt['quantita'])
        print(ddt['ubicazione']) 
        print(ddt['descrizione']) 
        print(ddt['ddt']) 
        print(ddt['data_ordine']) 
        print(ddt['fornitore'])
        print(ddt['arrivato'])
        print(ddt['data_arrivo_ordine'])

    # Dove vedere l'output?
    # L'output di "print()" verrà visualizzato nel terminale in cui esegui l'applicazione Flask. Se usi un ambiente di sviluppo come Visual Studio Code, l'output potrebbe essere visualizzato nel pannello "Debug Console" o "Terminal".

    connection.close()
    return render_template('show_ddt.html', ddts=ddts)
##########################################################


# Show rdas
@app.route('/show_rdas')
@login_required
def show_rdas():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM example")
    rdas = cursor.fetchall()

    # debug
    print(rdas)
    print(type(rdas))

    for rda in rdas:
        print(rda)
        print(rda['id'])
        print(rda['rda'])
        print(rda['basket_name'])
        print(rda['fornitore'])
        print(rda['importo_sc'])
        print(rda['oda'])
        print(rda['commessa'])
        print(rda['element'])
        print(rda['richiedente'])
        print(rda['data_creazione'])
        print(rda['tipologia_acquisto'])

    connection.close()
    return render_template('show_rda.html', rdas=rdas)
##########################################################


# Show fornitori
@app.route('/show_fornitori')
@login_required
def show_fornitori():
    connection = get_fornitori_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM fornitori")
    fornitori = cursor.fetchall()

    # debug
    print(fornitori)
    print(type(fornitori))

    for fornitore in fornitori:
        print(fornitore)
        print(fornitore['id'])

    connection.close()
    return render_template('fornitori.html', fornitori=fornitori)
##########################################################



# Add ddt
@app.route('/add_ddt', methods=['POST'])
def add_ddt():
    data = request.get_json()
    new_ddt = data.get('ddt')

    if new_ddt:
        connection = get_ddt_db_connection()
        cursor = connection.cursor()
        cursor.execute("INSERT OR IGNORE INTO ddt (fornitore) VALUES (?)", (new_ddt,))
        connection.commit()
        connection.close()

        return {"success": True}
    return {"success": False}, 400
##########################################################


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
##########################################################


# Restituire elenco fornitori
@app.route('/get_fornitori', methods=['GET'])
def get_fornitori():
    connection = get_fornitori_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT fornitore FROM fornitori")
    fornitori = [row['fornitore'] for row in cursor.fetchall()]
    connection.close()
    return jsonify({"fornitori": fornitori})
##########################################################

# Modify
@app.route('/modify')
def modify():
    return render_template('modify.html')
##########################################################


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
##########################################################


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
##########################################################


# Assicurati che la tabella example nel tuo database SQLite abbia effettivamente le colonne che stai cercando di aggiornare. Puoi farlo eseguendo una query per visualizzare la struttura della tabella
@app.route('/check_table_structure')
def check_table_structure():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("PRAGMA table_info(example)")
    columns = cursor.fetchall()
    connection.close()
    return jsonify([dict(column) for column in columns]), 200
##########################################################


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
##########################################################


# Search
@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    if request.method == 'POST':
        search_field = request.form['search_field']
        search_value = request.form['search_value']

        if search_field and search_value:
            connection = get_db_connection()
            cursor = connection.cursor()

            # Dynamically construct the SQL query
            query = f"SELECT * FROM example WHERE {search_field} = ?"
            cursor.execute(query, (search_value,))
            results = cursor.fetchall()
            connection.close()

            return render_template('search.html', results=results)

    return render_template('search.html')
##########################################################

# Search DDT
@app.route('/search_ddt', methods=['GET', 'POST'])
@login_required
def search_ddt():
    if request.method == 'POST':
        search_field = request.form['search_field']
        search_value = request.form['search_value']

        if search_field and search_value:
            connection = get_ddt_db_connection()
            cursor = connection.cursor()

            # Dynamically construct the SQL query
            query = f"SELECT * FROM example WHERE {search_field} = ?"
            cursor.execute(query, (search_value,))
            results = cursor.fetchall()
            connection.close()

            return render_template('search_ddt.html', results=results)

    return render_template('search_ddt.html')
##########################################################


# Search Results
@app.route('/search_results', methods=['GET'])
def search_results():
    search_field = request.args.get('search_field')
    search_value = request.args.get('search_value')

    if not search_field or not search_value:
        return jsonify({"error": "Please select a search field and enter a value."}), 400 

    connection = get_db_connection()
    if connection is None:
        return jsonify({"error": "Database connection error"}), 500

    try:
        cursor = connection.cursor()
        query = f"SELECT * FROM example WHERE {search_field} = ?"
        cursor.execute(query, (search_value,))
        results = cursor.fetchall()
        return jsonify([dict(row) for row in results]), 200  # Return results as JSON

    except sqlite3.Error as e:
        print(f"Database error during search: {e}")
        return jsonify({"error": "An error occurred during the search. Please try again."}), 500
    finally:
        connection.close()
##########################################################

# Search Results DDT
@app.route('/search_results_ddt', methods=['GET'])
def search_results_ddt():
    search_field = request.args.get('search_field')
    search_value = request.args.get('search_value')

    if not search_field or not search_value:
        return jsonify({"error": "Please select a search field and enter a value."}), 400

    connection = get_ddt_db_connection()
    if connection is None:
        return jsonify({"error": "Database connection error"}), 500

    try:
        cursor = connection.cursor()
         # Query per cercare nella tabella ddt
        query = f"SELECT * FROM ddt WHERE {search_field} = ?"  
        cursor.execute(query, (search_value,))
        results = cursor.fetchall()
        return jsonify([dict(row) for row in results]), 200  # Return results as JSON
    except sqlite3.Error as e:
        print(f"Database error during search: {e}")
        return jsonify({"error": "An error occurred during the search. Please try again."}), 500
    finally:
            connection.close()


# non dimenticare di cambiarlo in False prima di caricarlo sull'host per evitare qualsiasi attacco da parte di hacker
if __name__ == "__main__":
    app.run(debug=True)
