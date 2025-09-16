from flask import Flask, redirect, url_for, session
from modules.database.manager import create_sqlite_tables, connect_to_db, finish_connection
from modules.routes.dashboard import dashboard_bp
from modules.routes.auth import auth_bp
import os

# ===============================
# Configuração inicial do Flask e Banco de Dados
# ===============================
create_sqlite_tables()  # Criação das tabelas SQLite, caso não existam
app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.secret_key = os.getenv("SECRET_KEY")

# ===============================
# Registro dos Blueprints
# ===============================
app.register_blueprint(dashboard_bp, url_prefix="/dashboard")
app.register_blueprint(auth_bp)

# ===============================
# Rota de Logout
# ===============================
@app.route("/logout")
def logout():
    if "user_login" in session or "session_token" in session:
        connection, cursor = connect_to_db()
        try:
            user_login = session.get("user_login")
            cursor.execute(
                "UPDATE users_login SET session_token = NULL WHERE login = ?",
                (user_login[0],)
            )
            connection.commit()
        finally:
            finish_connection(connection, cursor)

        session.clear()

    return redirect(url_for("auth.login_page"))

# ===============================
# Tratamento de erro 404
# ===============================
@app.errorhandler(404)
def page_not_found(e):
    if "session_token" in session and "user_login" in session:
        return redirect(url_for("dashboard.home_page"))
    else:
        return redirect(url_for("auth.login_page"))

# ===============================
# Inicialização da aplicação
# ===============================
if __name__ == "__main__":
    app.run(debug=True)