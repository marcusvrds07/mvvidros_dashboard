from flask import Blueprint, render_template, request, session, redirect, url_for
from modules.services.auth_service import register_user, login_user, send_recovery_code, reset_user_password
from modules.core.auth_decorators import logout_required
from modules.database.manager import connect_to_db, finish_connection
import bcrypt, datetime

auth_bp = Blueprint("auth", __name__, url_prefix="")

@auth_bp.route("/login", methods=["GET", "POST"])
@logout_required
def login_page():
    connection, cursor = connect_to_db()
    cursor.execute("SELECT COUNT(*) FROM users_login")
    have_users = cursor.fetchone()[0] > 0
    finish_connection(connection, cursor)

    context = {"have_users": have_users, "title": "Login"}

    if request.method == "POST":
        if have_users:
            if "login" in request.form and "login-password" in request.form:
                return login_user(context)
            else:
                context["error"] = "Cadastro bloqueado."
                return render_template("login.html", context=context)
        else:
            if "signup-login" in request.form and "signup-password" in request.form:
                return register_user()
            else:
                context["error"] = "Erro na hora de validar"
                return render_template("login.html", context=context)

    return render_template("login.html", context=context)

@auth_bp.route("/recovery_password", methods=["GET", "POST"])
@logout_required
def recovery_password():
    return send_recovery_code()

@auth_bp.route("/reset_password", methods=["GET", "POST"])
@logout_required
def reset_password_page():
    if "confirmed_user_id" in session or (request.method == "POST" and session.get("first_login", False)):
        return reset_user_password()
    else:
        return redirect(url_for("auth.login_page"))

@auth_bp.route("/verify_code", methods=["GET", "POST"])
@logout_required
def verify_code():
    context = {
        'valid_code': session.pop('valid_code', None),
        'title': 'Verificar Código'
    }

    if request.method == "POST":
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        connection, cursor = connect_to_db()

        try:
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
                if stored_hash and bcrypt.checkpw(code, stored_hash.encode("utf-8")):
                    cursor.execute('UPDATE passwords_resets SET used = 1 WHERE id = ?', (id,))
                    connection.commit()

                    session['confirmed_user_id'] = id_login
                    session.pop('id_password_reset')

                    return redirect(url_for('auth.reset_password_page'))
                else:
                    context["error"] = "Código inválido"
            else:
                return redirect(url_for('auth.recovery_password'))

            return render_template("verify_code.html", context=context)
        finally:
             finish_connection(connection, cursor)
    if "id_password_reset" in session:
        return render_template("verify_code.html", context=context)
    else:
        return redirect(url_for('auth.recovery_password'))
