from flask import redirect, url_for, session
from modules.manager_database import connect_to_db, finish_connection
from functools import wraps


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "session_token" not in session or "user_login" not in session:
            return redirect(url_for("logout"))

        connection, cursor = connect_to_db()
        cursor.execute('SELECT session_token FROM users_login WHERE login = ?', (session.get('user_login', ''),))
        row = cursor.fetchone()
        db_token = row[0] if row else None
        finish_connection(connection, cursor)

        if not db_token or db_token != session.get("session_token"):
            session.clear()
            return redirect(url_for("login"))

        return f(*args, **kwargs)
    return decorated_function

def logout_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "session_token" in session or "user_login" in session:
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function
