import bcrypt, uuid, random, datetime
from flask import request, session, redirect, url_for, flash, render_template
from modules.database.manager import connect_to_db, finish_connection, insert_password_at_database
from modules.core.validations import password_validator, email_validator
from modules.services.email_service import send_email

# ===============================
# Register user
# ===============================
def register_user():
    signup_login = request.form.get("signup-login", "").strip().lower()
    signup_password = request.form.get("signup-password", "").strip()

    if email_validator(signup_login):
        if password_validator(signup_password):
            signup_password = bcrypt.hashpw(signup_password.encode(), bcrypt.gensalt())
            try:
                insert_password_at_database(signup_login, signup_password, False)
                flash("Conta criada com sucesso!", "success")
                return redirect(url_for("auth.login_page"))
            except:
                flash("Não foi possível criar sua conta!", "error")
        else:
            return render_template("login.html", context={"error": "Senha inválida"})
    else:
        return render_template("login.html", context={"error": "Email inválido"})


# ===============================
# Authenticate user
# ===============================
def login_user(context):
    login = request.form.get("login", "").strip()
    login_password = request.form.get("login-password", "").strip().encode("utf8")

    connection, cursor = connect_to_db()
    cursor.execute("SELECT id, password, first_login FROM users_login WHERE login = ?", (login,))
    id, db_hashed_password, first_login = cursor.fetchone() or (None, None, None)

    if db_hashed_password is not None:
        hashed_password = db_hashed_password.encode("utf-8") if isinstance(db_hashed_password, str) else db_hashed_password

        if bcrypt.checkpw(login_password, hashed_password):
            session["session_token"] = str(uuid.uuid4())
            session["user_login"] = (login, id)

            cursor.execute("SELECT ui.id, ui.full_name FROM users_info as ui JOIN users_login as ul ON ul.id = ui.id_login")
            user_info = cursor.fetchone()

            cursor.execute(
                "UPDATE users_login SET session_token = ? WHERE login = ?",
                (session.get("session_token", ""), login,)
            )
            connection.commit()
            finish_connection(connection, cursor)

            if first_login:
                session["first_login"] = True
            if not user_info:
                session["no_user_info"] = True

            return redirect(url_for("dashboard.home_page"))

    finish_connection(connection, cursor)
    context["error"] = "Usuário ou senha inválido"
    return render_template("login.html", context=context)


# ===============================
# Send recovery code
# ===============================
def send_recovery_code():
    context = {"title": "Recuperação de Senha"}
    connection, cursor = connect_to_db()

    try:
        if request.method == "POST":
            now = datetime.datetime.now()
            recovery_code = str(random.randint(100000, 999999))
            reset_email = request.form.get("reset_email", "").strip().lower()

            cursor.execute(
                '''SELECT ul.id, ul.login, pr.id, pr.id_login
                   FROM users_login as ul
                   LEFT JOIN passwords_resets as pr 
                   ON pr.id_login = ul.id AND pr.used = 0 AND expired_at > ?
                   WHERE login = ?''',
                (now.strftime("%Y-%m-%d %H:%M:%S"), reset_email)
            )

            result = cursor.fetchone()

            if not result:
                context["error"] = "Erro ao enviar o e-mail"
                return render_template("recovery_password.html", context=context)

            id_login, email_recovery, id_password_reset, pr_id_login = result

            if not session.get("confirmed_user_id", "") == id_login:
                if id_password_reset is None and email_recovery:
                    email_template = f"""
                    <html>
                    <body>
                        <h2>Olá, {email_recovery}!</h2>
                        <p>Você solicitou a recuperação de senha.</p>
                        <p>Digite o código abaixo para continuar:</p>
                        <div>{' '.join([f'<b>{digit}</b>' for digit in recovery_code])}</div>
                        <p>Se você não fez essa solicitação, ignore este email.</p>
                    </body>
                    </html>
                    """
                    try:
                        send_email(email_recovery, "Redefinição de Senha", email_template)

                        hashed_code = bcrypt.hashpw(recovery_code.encode(), bcrypt.gensalt()).decode()

                        cursor.execute(
                            "INSERT INTO passwords_resets (id_login, code_hash, expired_at, used) VALUES (?, ?, ?, ?)",
                            (id_login, hashed_code, (now + datetime.timedelta(minutes=10)).strftime("%Y-%m-%d %H:%M:%S"), False)
                        )
                        id_password_reset = cursor.lastrowid
                        connection.commit()

                        session["id_password_reset"] = id_password_reset
                        return redirect(url_for("auth.verify_code"))
                    except:
                        context["error"] = "Erro ao enviar o e-mail"
                else:
                    session["id_password_reset"] = id_password_reset
                    session["valid_code"] = True
                    return redirect(url_for("auth.verify_code"))
            else:
                return redirect(url_for("auth.reset_password_page"))
        return render_template("recovery_password.html", context=context)
    finally:
        finish_connection(connection, cursor)



# ===============================
# Reset password
# ===============================
def reset_user_password():
    context = {"title": "Redefinir Senha"}
    connection, cursor = connect_to_db()

    if request.method == "POST":
        password = request.form.get("password", "").strip()
        confirm_password = request.form.get("password-confirm", "").strip()

        if password == confirm_password:
            if password_validator(password):
                password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
                if not session.get("first_login", False):
                    cursor.execute(
                        "UPDATE users_login SET password = ?, first_login = ? WHERE id = ?",
                        (password, False, session.pop("confirmed_user_id", ""))
                    )
                else:
                    user_login = session.get("user_login")
                    cursor.execute(
                        "UPDATE users_login SET password = ?, first_login = ? WHERE login = ?",
                        (password, False, user_login[0])
                    )
                connection.commit()
                finish_connection(connection, cursor)

                if session.pop("first_login", False):
                    return redirect(url_for("dashboard.home_page"))
                return redirect(url_for("auth.login_page"))
            else:
                context["error"] = "Senha inválida"
        else:
            context["error"] = "As senhas não são iguais"

    return render_template("reset_password.html", context=context)
