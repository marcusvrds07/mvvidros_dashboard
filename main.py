from flask import Flask, render_template, request, redirect, url_for, session, flash
from modules.manager_database import create_sqlite_tables, connect_to_db, finish_connection
from modules.auth import user_register, user_login, send_code, reset_password
from modules.utils.required import login_required, logout_required
from modules.utils.base_context import dashboard_context_base
from modules.dashboard import users, home_page
import os, bcrypt, datetime


# ===============================
# Configuração inicial do Flask e Banco de Dados
# ===============================
create_sqlite_tables()  # Criação das tabelas SQLite, caso não existam
app = Flask(__name__)
app.config['SESSION_PERMANENT'] = False
app.secret_key = os.getenv("SECRET_KEY")


# ===============================
# Rota de Login / Cadastro
# ===============================
@app.route("/login", methods=["GET", "POST"])
@logout_required
def login():
    connection, cursor = connect_to_db()
    cursor.execute('SELECT COUNT(*) FROM users_login')
    have_users = True if cursor.fetchone()[0] > 0 else False

    context = {
        'have_users': have_users,
        'title': 'Login'
    }

    if request.method == "POST":
        if have_users:
            # Fluxo de login
            if "login" in request.form and "login-password" in request.form:
                return user_login(context)
            else:
                context['error'] = "Cadastro bloqueado."
                return render_template("login.html", context=context)
        else:
            # Fluxo de cadastro inicial (primeiro usuário do sistema)
            if "signup-login" in request.form and "signup-password" in request.form:
                return user_register()
            else:
                context['error'] = "Erro na hora de validar"
                return render_template("login.html", context=context)
    return render_template("login.html", context=context)


# ===============================
# Rota de Recuperação de Senha
# ===============================
@app.route("/recovery_password", methods=["GET", "POST"])
@logout_required
def recovery_password():
    return send_code()

# ===============================
# Rota de Verificação de Código de Recuperação de Senha
# ===============================
@app.route("/verify_code", methods=['GET', 'POST'])
@logout_required
def verify_code():
    context = {
        'valid_code': session.pop('valid_code', None),
        'title': 'Verificar Código'
    }

    if request.method == 'POST':
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        connection, cursor = connect_to_db()

        # Concatena os dígitos do formulário de verificar senha
        code = "".join([request.form.get(f"n{i}") for i in range(1, 7)]).encode()

        cursor.execute(
            '''SELECT code_hash, id, id_login 
               FROM passwords_resets 
               WHERE id = ? AND expired_at > ? AND used = 0''',
            (session.get('id_password_reset'), now)
        )
        stored_hash = cursor.fetchone()

        if stored_hash:
            stored_hash, id, id_login = stored_hash
            # Valida se o código informado bate com o do banco
            if stored_hash and bcrypt.checkpw(code, stored_hash.encode("utf-8")):
                cursor.execute('UPDATE passwords_resets SET used = 1 WHERE id = ?', (id,))
                connection.commit()

                # Salva usuário confirmado para resetar senha
                session['confirmed_user_id'] = id_login
                session.pop('id_password_reset')

                return redirect(url_for('reset_password_page'))
            else:
                context["error"] = "Código inválido"
        else:
            return redirect(url_for('recovery_password'))

        return render_template("verify_code.html", context=context)

    # Caso exista reset em andamento
    if "id_password_reset" in session:
        return render_template("verify_code.html", context=context)
    else:
        return redirect(url_for('recovery_password'))


# ===============================
# Rota de Redefinição de Senha
# ===============================
@app.route("/reset_password", methods=['GET', 'POST'])
@logout_required
def reset_password_page():
    if 'confirmed_user_id' in session or (request.method == 'POST' and session.get('first_login', False)):
        return reset_password()
    else:
        return redirect(url_for('login'))


# ===============================
# Rotas da Dashboard (restrita a usuários logados)
# ===============================
@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    return home_page()

@app.route("/dashboard/vendas", methods=["GET", "POST"])
@login_required
def dashboard_sales():
    context = dashboard_context_base('Suas Vendas')
    return render_template("dashboard/sales.html", context=context)

@app.route("/dashboard/estoque", methods=["GET", "POST"])
@login_required
def dashboard_stock():
    context = dashboard_context_base('Estoque')
    return render_template("dashboard/stock.html", context=context)

@app.route("/dashboard/usuarios", methods=["GET", "POST"])
@login_required
def dashboard_users():
    return users()

# ===============================
# Rota de Logout
# ===============================
@app.route("/logout")
def logout():
    if "user_login" in session or "session_token" in session:
        connection, cursor = connect_to_db()
        user_login = session.get('user_login')
        cursor.execute(
            "UPDATE users_login SET session_token = NULL WHERE login = ?",
            (user_login[0],)
        )
        connection.commit()
        finish_connection(connection, cursor)

        session.clear()

    return redirect(url_for("login"))


# ===============================
# Tratamento de erro 404
# ===============================
@app.errorhandler(404)
def page_not_found(e):
    if "session_token" in session and "user_login" in session:
        return redirect(url_for("dashboard"))
    else:
        return redirect(url_for("login"))


# ===============================
# Inicialização da aplicação
# ===============================
if __name__ == "__main__":
    app.run(debug=True)