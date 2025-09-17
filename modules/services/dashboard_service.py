from modules.services.email_service import send_email
from modules.core.validations import email_validator
import sqlite3, smtplib, bcrypt, secrets, string
from modules.database.manager import connect_to_db, finish_connection, insert_password_at_database
from modules.core.validations import check_name, check_date, check_cpf, check_phone_number

def generate_password(size=10):
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(size))

def create_user(email):
    email = email.strip().lower()
    if not email_validator(email):
        return {"success": False, "error": "O email precisa ser válido!"}

    temporary_password = generate_password()
    password = bcrypt.hashpw(temporary_password.encode(), bcrypt.gensalt())

    try:
        insert_password_at_database(email, password, True)
        send_email(email, "Cadastro Realizado", temporary_password)
        return {"success": True}
    except sqlite3.IntegrityError as e:
        if "UNIQUE constraint failed" in str(e):
            return {"success": False, "field": "email_error", "error": "O email já existe em nosso banco de dados!"}
    except smtplib.SMTPRecipientsRefused:
        return {"success": False, "field": "email_error", "error": "Destinatário inválido!"}
    except smtplib.SMTPException:
        return {"success": False, "error": "Erro ao enviar e-mail!"}

def save_user_info(user_login, form):
    values = {
        "full_name_val": form.get("full_name", "").strip().title(),
        "date_val": form.get("date_of_birth", "").strip(),
        "cpf_val": form.get("cpf", "").strip(),
        "telephone_val": form.get("telephone_number", "").strip(),
        "position_val": form.get("position", "").strip()
    }

    full_name = check_name(values["full_name_val"])
    date_of_birth = check_date(values["date_val"])
    cpf = check_cpf(values["cpf_val"])
    phone_number = check_phone_number(values["telephone_val"])

    # Validações encadeadas
    if not full_name[0]:
        field, message = "name_error", "O nome é obrigatório"
    elif not date_of_birth[0]:
        field, message = "date_error", "A data de nascimento é inválida"
    elif not cpf[0]:
        field, message = "cpf_error", "O CPF informado é inválido"
    elif not phone_number[0]:
        field, message = "telephone_error", "O telefone informado é inválido"
    else:
        field, message = None, None

    if field:
        return {
            "success": False,
            "error_field": field,
            "message": message,
            "context_update": values
        }

    # Inserção no banco
    connection, cursor = connect_to_db()
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
        connection.commit()
    finally:
        finish_connection(connection, cursor)

    return {"success": True, "message": "As informações foram salvas com sucesso!"}