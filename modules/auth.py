import bcrypt, uuid
from modules.manager_database import connect_to_db, finish_connection
from flask import request, redirect, url_for, session, flash, render_template

def user_register(context):
    salt = bcrypt.gensalt() 
    connection, cursor = connect_to_db()
    signup_login = request.form.get("signup-login", "").strip()
    signup_password = bcrypt.hashpw(request.form.get("signup-password", "").strip().encode(), salt)
    # realizar validação da senha e do email via backend
    try:
        cursor.execute('INSERT INTO users_login (login, password) VALUES (?, ?)', (signup_login, signup_password,))
        
        connection.commit()
        finish_connection(connection, cursor)

        flash("Conta criada com sucesso!")
        # logica após registo da senha:

        # return redirect(url_for("login"))
    except:
        flash("Não foi possivel criar sua conta!")

def user_login(context):
    login = request.form.get("login", "").strip()
    login_password = request.form.get("login-password", "").strip().encode('utf8')
    connection, cursor = connect_to_db()

    cursor.execute('SELECT password FROM users_login WHERE login = ?', (login,))
    hashed_password = cursor.fetchone()

    if hashed_password is not None:
        hashed_password = hashed_password[0]
        if isinstance(hashed_password, str):
            hashed_password = hashed_password.encode("utf-8")

        if bcrypt.checkpw(login_password, hashed_password):
            session["user"] = login
            finish_connection(connection, cursor)
            return redirect(url_for("dashboard"))

    finish_connection(connection, cursor)
    context['error'] = 'Usuario ou Senha invalido'
    return render_template("login.html", context=context)



