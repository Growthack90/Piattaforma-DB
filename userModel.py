from flask_login import UserMixin

# Simulazione di un database di utenti (da sostituire con un database reale)
users = {
    'admin': {'password': 'password123'},
    'utente1': {'password': '123'}
}

class User(UserMixin):
    def __init__(self, username):
        self.id = username
    
    @staticmethod
    def get(username):
        user = users.get(username)
        if user:
            return User(username)
        return None

    # È stato aggiunto il metodo "create" alla classe "User" per gestire la creazione di nuovi ACCOUNT utenti
    # La logica di registrazione è semplificata, ma in un'applicazione reale dovresti usare un database (come SQLite, PostgreSQL, MySQL) per memorizzare gli utenti in modo persistente
    # IMPORTANTE!:
     # - Sicurezza: In una vera applicazione, non dovresti mai memorizzare le password in chiaro come nell'esempio. Dovresti usare una funzione di hashing (come bcrypt o scrypt) per crittografare le password prima di memorizzarle nel database.
     # - Database: Sostituisci la simulazione del database users con un database reale per la persistenza dei dati.
     # - Validazione: Aggiungi la validazione dei dati inseriti dall'utente (ad esempio, lunghezza minima della password, formato dell'username) per migliorare la sicurezza e l'usabilità.

    # registrazione
    @staticmethod
    def create(username, password): 
        if username in users:
            return False  # Utente già esistente
        users[username] = {'password': password}
        return True

