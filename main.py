from flask import Flask, render_template, request, redirect, url_for, session, flash
from modules.manager_database import create_sqlite_tables, connect_to_db
from modules.auth import user_register, user_login, reset_password
import os, bcrypt

create_sqlite_tables()
app = Flask(__name__)
app.config['SESSION_PERMANENT'] = False
app.secret_key = os.getenv("SECRET_KEY")

@app.route("/login", methods=["GET", "POST"])
def login():
    connection, cursor = connect_to_db()
    cursor.execute('SELECT COUNT(*) FROM users_login')
    have_users = True if cursor.fetchone()[0] > 0 else False
    context = {
        'have_users': have_users,
    }

    if request.method == "POST":
        if have_users:
            if "login" in request.form and "login-password" in request.form:
                return user_login(context)
            else:
                context['error'] = "Login bloqueado até que o admin seja criado."
                return render_template("login.html", context=context)
        else:
            if "signup-login" in request.form and "signup-password" in request.form:
                user_register()
            else:
                context['error'] = "Erro na hora de validar"
                return render_template("login.html", context=context)
            
    if "user" not in session:
        return render_template("login.html", context=context)
    else:
        return redirect(url_for("dashboard"))

@app.route("/recovery_password", methods=["GET", "POST"])
def recovery_password():
    return reset_password()

@app.route('/')
def home():
    return redirect(url_for('login'))


@app.route("/verify_code", methods=['GET','POST'])
def verify_code():
    context= {}
    if request.method == 'POST':
        code = "".join([request.form.get(f"n{i}") for i in range(1, 7)]).encode()

        stored_hash = session.get("recovery_code")

        if stored_hash and bcrypt.checkpw(code, stored_hash.encode("utf-8")):
            context["error"] = "Código válido"
        else:
            context["error"] = "Código inválido"

        return render_template("recovery_password(code).html", context=context)
    return render_template("recovery_password(code).html", context=context)

@app.route("/dashboard")
def dashboard():
    if "user" in session:
        return render_template("dashboard.html")
    else:
        return redirect(url_for("login"))

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
