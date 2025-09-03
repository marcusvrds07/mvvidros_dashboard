from flask import Flask, render_template, request, redirect, url_for, session, flash
from modules.manager_database import create_sqlite_tables, connect_to_db
from modules.auth import user_register, user_login, send_code, reset_password
import os, bcrypt, datetime

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
    return send_code()

@app.route('/')
def home():
    return redirect(url_for('login'))


@app.route("/verify_code", methods=['GET','POST'])
def verify_code():
    context= {
        'valid_code': session.pop('valid_code', None)
    }
    if request.method == 'POST':
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        connection, cursor = connect_to_db()
        code = "".join([request.form.get(f"n{i}") for i in range(1, 7)]).encode()

        cursor.execute('SELECT code_hash, id, id_login FROM passwords_resets WHERE id = ? AND expired_at > ? AND used = 0', (session.get('id_password_reset'), now))
        stored_hash = cursor.fetchone()

        if stored_hash:
            stored_hash, id, id_login = stored_hash
            if stored_hash and bcrypt.checkpw(code, stored_hash.encode("utf-8")):
                cursor.execute('UPDATE passwords_resets SET used = 1 WHERE id = ? ', (id,))
                connection.commit()

                session['confirmed_user_id'] = id_login

                session.pop('id_password_reset')
                return redirect(url_for('reset_password_page'))
            else:
                context["error"] = "Código inválido"
        else:
            return redirect(url_for('recovery_password'))

        return render_template("verify_code.html", context=context)
    if "id_password_reset" in session:
        return render_template("verify_code.html", context=context)
    else:
        return redirect(url_for('recovery_password'))


@app.route("/reset_password", methods=['GET', 'POST'])
def reset_password_page():
    if 'confirmed_user_id' in session:
        return reset_password()
    else:
        return redirect(url_for('login'))

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
