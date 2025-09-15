import sqlite3, os
from pathlib import Path

# Criação das Tabelas do Banco de dados (SQLITE3)
def create_sqlite_tables():

    connection, cursor = connect_to_db()
    tables = [
        '''
        CREATE TABLE IF NOT EXISTS users_login (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        login TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        first_login BOOLEAN DEFAULT 0,
        session_token TEXT
    );
    ''',
        '''
        CREATE TABLE IF NOT EXISTS passwords_resets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_login INTEGER NOT NULL,
            code_hash TEXT NOT NULL,
            expired_at DATETIME NOT NULL,
            used BOOLEAN DEFAULT 0,

            FOREIGN KEY (id_login) REFERENCES users_login (id)
        )
    ''',
    '''
    CREATE TABLE IF NOT EXISTS users_info (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_login INTEGER UNIQUE NOT NULL,
        full_name TEXT NOT NULL,
        date_of_birth DATE NOT NULL,
        phone_number VARCHAR(20) NOT NULL,
        cpf VARCHAR(11) NOT NULL,
        position_in_company TEXT NOT NULL,
        FOREIGN KEY (id_login) REFERENCES users_login (id) ON DELETE CASCADE
    );
    '''
    ]

    for table in tables:
        cursor.execute(table)

    cursor.close()
    connection.close()

# Responsavel pela conexão e criação do cursor com a database
def connect_to_db():
    if not os.path.exists('database'):
        os.makedirs('database')

    ROOT_DIR = Path(__file__).parent.parent
    DB_NAME = 'database/login.db'
    DB_FILE = ROOT_DIR / DB_NAME

    connection = sqlite3.connect(DB_FILE, check_same_thread=False)
    cursor = connection.cursor()

    return connection, cursor

def finish_connection(connection, cursor):
    cursor.close()
    connection.close()

def insert_password_at_database(signup_login, signup_password, first_login):
    connection, cursor = connect_to_db()    
    
    # Inserção do novo usuário no banco de dados
    cursor.execute(
        'INSERT INTO users_login (login, password, first_login) VALUES (?, ?, ?)',
        (signup_login, signup_password, first_login)
    )
    connection.commit()
    finish_connection(connection, cursor)