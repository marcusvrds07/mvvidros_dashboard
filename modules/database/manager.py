import sqlite3
from pathlib import Path

# ===============================
# Configuração do caminho do banco
# ===============================
ROOT_DIR = Path.cwd()
DB_DIR = ROOT_DIR / "modules" / "database"
DB_DIR.mkdir(parents=True, exist_ok=True)

DB_FILE = DB_DIR / "mvvidros.db"


# ===============================
# Conexão com o banco
# ===============================
def connect_to_db():
    connection = sqlite3.connect(DB_FILE, check_same_thread=False)
    cursor = connection.cursor()
    return connection, cursor

def finish_connection(connection, cursor):
    cursor.close()
    connection.close()


# ===============================
# Criação das tabelas
# ===============================
def create_sqlite_tables():
    tables = [
        """
        CREATE TABLE IF NOT EXISTS users_login (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            login TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            first_login BOOLEAN DEFAULT 0,
            session_token TEXT
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS passwords_resets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_login INTEGER NOT NULL,
            code_hash TEXT NOT NULL,
            expired_at DATETIME NOT NULL,
            used BOOLEAN DEFAULT 0,
            FOREIGN KEY (id_login) REFERENCES users_login (id)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS users_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_login INTEGER UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            date_of_birth DATE NOT NULL,
            phone_number VARCHAR(20) NOT NULL,
            cpf VARCHAR(11) UNIQUE NOT NULL,
            position_in_company TEXT NOT NULL,
            FOREIGN KEY (id_login) REFERENCES users_login (id) ON DELETE CASCADE
        );
        """
    ]

    connection, cursor = connect_to_db()
    try:
        for table in tables:
            cursor.execute(table)
        connection.commit()
    finally:
        finish_connection(connection, cursor)


# ===============================
# Inserção de usuários
# ===============================
def insert_password_at_database(signup_login, signup_password, first_login):
    connection, cursor = connect_to_db()
    try:
        cursor.execute(
            """
            INSERT INTO users_login (login, password, first_login)
            VALUES (?, ?, ?)
            """,
            (signup_login, signup_password, first_login)
        )
        connection.commit()
    finally:
        finish_connection(connection, cursor)
