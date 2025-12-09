import sqlite3
from models import User

class Database:
    def __init__(self, db_name='users.db'):
        self.db_name = db_name
        self.init_db()

    def init_db(self):
        # Создать таблицу если не существует
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL,
                            email TEXT NOT NULL UNIQUE
                       )
                       ''')
        conn.commit()
        conn.close()

    def get_all_users(self):
        # Получить всех пользователей
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users')
        rows = cursor.fetchall()
        conn.close()
        return [User(row[0], row[1], row[2]) for row in rows]

    def get_user_by_id(self, user_id):
        # Получить пользователя по id
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()
        return User(row[0], row[1], row[2]) if row else None

    def add_user(self, name, email):
        # Добавить нового пользователя
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO users (name, email) VALUES (?, ?)',
                           (name, email))
            conn.commit()
            user_id = cursor.lastrowid
            conn.close()
            return user_id
        except sqlite3.IntegrityError:
            conn.close()
            return None
