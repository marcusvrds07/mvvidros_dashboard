from flask import Blueprint, render_template, request, session, flash
from modules.database.manager import connect_to_db, finish_connection
from modules.core.context import dashboard_context_base
from modules.core.validations import check_date
import secrets, bcrypt, string, sqlite3, smtplib
from modules.services.dashboard_service import create_user, save_user_info

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")

# -----------------------------------------
# Função auxiliar para gerar senha temporária
# -----------------------------------------
def generate_password(size=10):
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(size))


# -----------------------------------------
# HOME PAGE
# -----------------------------------------
@dashboard_bp.route("/", methods=["GET", "POST"])
def home_page():
    context = dashboard_context_base("Dashboard")

    if request.method == "POST" and "no_user_info" in session:
        user_login = session.get("user_login")
        result = save_user_info(user_login, request.form)

        if not result["success"]:
            context[result["error_field"]] = result["message"]
            context["no_user_info"] = True
        else:
            session.pop("no_user_info", None)
            flash(result["message"], "success")

    for key in ["first_login", "no_user_info"]:
        if session.get(key, False):
            context[key] = True

    return render_template("dashboard/index.html", context=context)


# -----------------------------------------
# VENDAS
# -----------------------------------------
@dashboard_bp.route("/vendas", methods=["GET", "POST"])
def dashboard_sales():
    context = dashboard_context_base("Suas Vendas")
    return render_template("dashboard/sales.html", context=context)


# -----------------------------------------
# ESTOQUE
# -----------------------------------------
@dashboard_bp.route("/estoque", methods=["GET", "POST"])
def dashboard_stock():
    context = dashboard_context_base("Estoque")
    return render_template("dashboard/stock.html", context=context)


# -----------------------------------------
# USERS
# -----------------------------------------
@dashboard_bp.route("/usuarios", methods=["GET", "POST"])
def dashboard_users():
    context = dashboard_context_base("Gerencie Usuários")

    if request.method == "POST":
        result = create_user(request.form.get("email", ""))
        if not result["success"]:
            context["email_error"] = result["error"]

    # listar usuários
    connection, cursor = connect_to_db()
    cursor.execute("""
        SELECT ui.full_name, ui.cpf, ui.phone_number, ul.login, 
               ui.date_of_birth, ui.position_in_company
        FROM users_login as ul
        JOIN users_info as ui ON ui.id_login = ul.id
    """)
    keys = ["name", "cpf", "phone", "email", "birth_date", "position"]
    users_info = [dict(zip(keys, u)) for u in cursor.fetchall()]

    for user in users_info:
        user["birth_date"] = check_date(user.get("birth_date", ""), True)

    context["users_info"] = users_info
    finish_connection(connection, cursor)

    return render_template("dashboard/users.html", context=context)
