import sqlite3, os
from pathlib import Path

# Criação das Tabelas do Banco de dados (SQLITE3 ou MYSQL)
def create_sqlite_tables():

    connection, cursor = connect_to_db()
    tables = [
        '''
        CREATE TABLE IF NOT EXISTS users_login (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        login TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
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