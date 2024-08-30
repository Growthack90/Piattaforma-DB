from flask_login import UserMixin

# Simulazione di un database di utenti
users = {
    'admin': {'password': 'password123'}
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
