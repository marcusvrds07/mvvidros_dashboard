from modules.services.email_service import send_email
from modules.core.validations import email_validator
import sqlite3, smtplib, bcrypt, secrets, string
from modules.database.manager import connect_to_db, finish_connection, insert_password_at_database
from modules.core.validations import check_name, check_date, check_cpf, check_phone_number
from flask import request

def generate_password(size=10):
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(size))

def create_user(form):
    email = form.get("email", "").strip().lower()
    if not email_validator(email):
        return {"success": False, "field": "email_error", "message": "O email precisa ser válido!"}

    temporary_password = generate_password()
    password = bcrypt.hashpw(temporary_password.encode(), bcrypt.gensalt())

    connection, cursor = connect_to_db()
    try:
        cursor.execute(
            "INSERT INTO users_login (login, password, first_login) VALUES (?, ?, ?)",
            (email, password, True)
        )
        new_user_id = cursor.lastrowid

        result = save_user_info((email, new_user_id), form, connection, cursor)
        if not result["success"]:
            connection.rollback()
            return result

        send_email(email, "Cadastro Realizado", temporary_password)

        connection.commit()
        return {"success": True, "message": "Usuário criado com sucesso!"}

    except sqlite3.IntegrityError as e:
        connection.rollback()
        if "UNIQUE constraint failed" in str(e):
            return {"success": False, "field": "email_error", "message": "O email já existe em nosso banco de dados!"}
        return {"success": False, "field": "general_error", "message": "Erro no banco de dados"}
    except smtplib.SMTPException:
        connection.rollback()
        return {"success": False, "field": "email_error", "message": "Erro ao enviar e-mail!"}
    finally:
        finish_connection(connection, cursor)

def save_user_info(user_login, form, connection=None, cursor=None):
    close_connection = False
    if connection is None or cursor is None:
        connection, cursor = connect_to_db()
        close_connection = True

    values = {
        "full_name_val": form.get("full_name", "").strip().title(),
        "date_val": form.get("date_of_birth", "").strip(),
        "cpf_val": form.get("cpf", "").strip(),
        "telephone_val": form.get("telephone_number", "").strip(),
        "position_val": form.get("position", "").strip()
    }

    if not check_name(values["full_name_val"])[0]:
        return {"success": False, "field": "name_error", "message": "O nome informado inválido", "context_update": values}
    if not check_date(values["date_val"])[0]:
        return {"success": False, "field": "date_error", "message": "A data de nascimento é inválida", "context_update": values}
    if not check_cpf(values["cpf_val"])[0]:
        return {"success": False, "field": "cpf_error", "message": "O CPF informado é inválido", "context_update": values}
    if not check_phone_number(values["telephone_val"])[0]:
        return {"success": False, "field": "phone_error", "message": "O telefone informado é inválido", "context_update": values}

    try:
        cursor.execute(
            """
            INSERT INTO users_info 
                (id_login, full_name, date_of_birth, phone_number, cpf, position_in_company)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                user_login[1],
                values["full_name_val"],
                values["date_val"],
                values["telephone_val"],
                values["cpf_val"],
                values["position_val"]
            )
        )
        if close_connection:
            connection.commit()
    finally:
        if close_connection:
            finish_connection(connection, cursor)

    return {"success": True, "message": "As informações foram salvas com sucesso!"}