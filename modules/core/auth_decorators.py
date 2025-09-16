from flask import redirect, url_for, session, request
from modules.database.manager import connect_to_db, finish_connection
from functools import wraps


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "session_token" not in session or "user_login" not in session:
            return redirect(url_for("logout"))
        
        if (session.get('first_login', False) and request.endpoint != "dashboard") or session.get('no_user_info', False) and request.endpoint != "dashboard":
            return redirect(url_for("dashboard.home_page"))

        connection, cursor = connect_to_db()
        user_login = session.get('user_login')
        cursor.execute('SELECT session_token FROM users_login WHERE login = ?', (user_login[0],))
        row = cursor.fetchone()
        db_token = row[0] if row else None
        finish_connection(connection, cursor)

        if not db_token or db_token != session.get("session_token"):
            session.clear()
            return redirect(url_for("auth.login_page"))

        return f(*args, **kwargs)
    return decorated_function

def logout_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if ("session_token" in session or "user_login" in session) and 'first_login' not in session:
            return redirect(url_for("dashboard.home_page"))
        return f(*args, **kwargs)
    return decorated_function
