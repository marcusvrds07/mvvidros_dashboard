from flask import Flask, render_template, request, redirect, url_for, session, flash
from modules.manager_database import insert_password_at_database, connect_to_db, finish_connection
from modules.utils.base_context import dashboard_context_base
import secrets, bcrypt, string
from modules.utils.utils import send_email

def generate_password(size=10):
    character = string.ascii_letters + string.digits
    return ''.join(secrets.choice(character) for _ in range(size))

def users():
    context = dashboard_context_base('Gerencie Usuários')
    if request.method == 'POST':
        email = request.form.get("email", "").strip()
        temporary_password = generate_password()
        password = bcrypt.hashpw(temporary_password.encode(), bcrypt.gensalt())
        insert_password_at_database(email, password, True)

        try:
            send_email(email, 'Cadastro Realizado', temporary_password)
        except:
            context['error'] = 'Error ao enviar o email'
    
    connection, cursor = connect_to_db()

    cursor.execute('SELECT login, password FROM users_login')
    users_info = cursor.fetchall()

    context['users_info'] = users_info

    print(users_info)

    finish_connection(connection, cursor)
    return render_template("dashboard/users.html", context=context)