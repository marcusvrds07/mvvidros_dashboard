from flask import Flask, render_template, request, redirect, url_for, session, flash
from modules.manager_database import insert_password_at_database, connect_to_db, finish_connection
from modules.utils.base_context import dashboard_context_base
import secrets, bcrypt, string, sqlite3,smtplib
from modules.utils.utils import send_email
from modules.utils.validations import email_validator, check_cpf, check_date, check_phone_number, check_name

def generate_password(size=10):
    character = string.ascii_letters + string.digits
    return ''.join(secrets.choice(character) for _ in range(size))

def home_page():
    context = dashboard_context_base('Dashboard')

    if request.method == 'POST':
        full_name_val = request.form.get("full_name", "").strip().title()
        date_of_birth_val = request.form.get("date_of_birth", "").strip()
        cpf_val = request.form.get("cpf", "").strip()
        telephone_val = request.form.get("telephone_number", "").strip()
        position_val = request.form.get("position", "").strip()

        full_name = check_name(full_name_val)
        date_of_birth = check_date(date_of_birth_val)
        cpf = check_cpf(cpf_val)
        telephone_number = check_phone_number(telephone_val)

        context.update({
            "full_name_val": full_name_val,
            "date_val": date_of_birth_val,
            "cpf_val": cpf_val,
            "telephone_val": telephone_val,
            "position_val": position_val
        })

        if not full_name[0]:
            context['name_error'] = full_name[1]
            context['no_user_info'] = True
        elif not date_of_birth[0]:
            context['date_error'] = date_of_birth[1]
            context['no_user_info'] = True
        elif not cpf[0]:
            context['cpf_error'] = cpf[1]
            context['no_user_info'] = True
        elif not telephone_number[0]:
            context['telephone_error'] = telephone_number[1]
            context['no_user_info'] = True
        else:
            session.pop('no_user_info', None)
            flash("As informações foram salvas com sucesso!", "error")
            # falta salvar as coisa na bd
        
    for key in ["first_login", "no_user_info"]:
        if session.get(key, False):
            context[key] = True

    return render_template("dashboard/index.html", context=context)

def users():
    context = dashboard_context_base('Gerencie Usuários')
    if request.method == 'POST':
        email = request.form.get("email", "").strip().lower()
        temporary_password = generate_password()
        password = bcrypt.hashpw(temporary_password.encode(), bcrypt.gensalt())

        if email_validator(email):
            try:
                insert_password_at_database(email, password, True)
                send_email(email, 'Cadastro Realizado', temporary_password)
            except sqlite3.IntegrityError as e:
                if "UNIQUE constraint failed" in str(e):
                    context['email_error'] = "O email ja existe em nosso banco de dados!"
            except smtplib.SMTPRecipientsRefused:
                context['email_error'] = 'Destinatario Inválido!'
            except smtplib.SMTPException as e:
                context['email_error'] = f"Erro ao enviar e-mail!"
            
            # salvamento de dados da tabela users_info
        else:
            context['email_error'] = 'O email precisa ser válido!'
        
        
    # Visualizar Lista de usuarios cadastrados
    connection, cursor = connect_to_db()
    cursor.execute('SELECT login, password FROM users_login')
    users_info = cursor.fetchall()
    context['users_info'] = users_info

    finish_connection(connection, cursor)
    return render_template("dashboard/users.html", context=context)