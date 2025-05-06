import sqlite3
from werkzeug.security import generate_password_hash

def init_db():
    conn = sqlite3.connect('elibrary.db')
    c = conn.cursor()
    # Drop the users and books tables if they exist to reset credentials and books
    c.execute('DROP TABLE IF EXISTS users')
    c.execute('DROP TABLE IF EXISTS books')
    c.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('student', 'admin'))
        )
    ''')
    c.execute('''
        CREATE TABLE books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_name TEXT NOT NULL,
            author_name TEXT NOT NULL
        )
    ''')
    # Insert both admin accounts and the specified student accounts
    users = [
        ('khusboo', generate_password_hash('khusi123'), 'admin'),
        ('pulkitberwal', generate_password_hash('pulkit123'), 'admin'),
        ('deepanshu', generate_password_hash('deepanshu123'), 'student'),
        ('khemraj', generate_password_hash('khemraj123'), 'student'),
        ('shubham', generate_password_hash('shubham123'), 'student'),
        ('shivam', generate_password_hash('shivam123'), 'student'),
        ('akhil', generate_password_hash('akhil123'), 'student')
    ]
    c.executemany('INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)', users)
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print('Database reset and initialized with new credentials and books table.')
