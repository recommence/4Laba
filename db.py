import sqlite3

class Database:
    def __init__(self, db_name):
        self.db_name = db_name
        self.connection = None
        self.cursor = None

    def connect(self):
        if not self.connection:
            self.connection = sqlite3.connect(self.db_name)
            self.cursor = self.connection.cursor()

    def disconnect(self):
        if self.connection:
            self.cursor.close()
            self.connection.close()
            self.connection = None
            self.cursor = None

    def init_db(self):
        self.connect()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL
            )
        ''')
        self.connection.commit()

    def add_user(self, name, email):
        self.connect()
        try:
            self.cursor.execute('INSERT INTO users (name, email) VALUES (?, ?)', (name, email))
            self.connection.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError:
            raise ValueError("User with this email already exists")

    def get_user(self, user_id):
        self.connect()
        self.cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        return self.cursor.fetchone()

    def get_all_users(self):
        self.connect()
        self.cursor.execute('SELECT * FROM users')
        return [{'id': row[0], 'name': row[1], 'email': row[2]} for row in self.cursor.fetchall()]

    def update_user(self, user_id, name, email):
        self.connect()
        self.cursor.execute('UPDATE users SET name = ?, email = ? WHERE id = ?', (name, email, user_id))
        self.connection.commit()
        return self.cursor.rowcount > 0

    def delete_user(self, user_id):
        self.connect()
        self.cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
        self.connection.commit()
        return self.cursor.rowcount > 0

