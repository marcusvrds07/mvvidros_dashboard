from flask import Blueprint, render_template, request, session, flash, redirect, url_for, get_flashed_messages
from modules.database.manager import connect_to_db, finish_connection
from modules.core.context import dashboard_context_base
from modules.core.validations import check_date
import secrets, bcrypt, string, sqlite3, smtplib
from modules.services.dashboard_service import create_user, save_user_info
from modules.core.auth_decorators import login_required

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
@login_required
def home_page():
    context = dashboard_context_base("Dashboard")

    if request.method == "POST" and "no_user_info" in session:
        user_login = session.get("user_login")
        result = save_user_info(user_login, request.form)

        if not result["success"]:
            context.update(result["context_update"])
            context[result["field"]] = result["message"]
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
@login_required
def dashboard_sales():
    context = dashboard_context_base("Suas Vendas")
    return render_template("dashboard/sales.html", context=context)


# -----------------------------------------
# ESTOQUE
# -----------------------------------------
@dashboard_bp.route("/estoque", methods=["GET", "POST"])
@login_required
def dashboard_stock():
    context = dashboard_context_base("Estoque")
    return render_template("dashboard/stock.html", context=context)


# -----------------------------------------
# USERS
# -----------------------------------------
@dashboard_bp.route("/usuarios", methods=["GET", "POST"])
@login_required
def dashboard_users():
    context = dashboard_context_base("Gerencie Usuários")

    if request.method == "POST":
        result = create_user(request.form)
        if not result["success"]:
            flash({"field": result["field"], "message": result["message"], "context_update": result.get("context_update", {})}, "form_error")
        else:
            flash(result["message"], "success")
        return redirect(url_for('dashboard.dashboard_users'))

    # listar usuários
    connection, cursor = connect_to_db()
    cursor.execute("""
        SELECT ul.id, ui.full_name, ui.cpf, ui.phone_number, ul.login, 
               ui.date_of_birth, ui.position_in_company
        FROM users_login as ul
        JOIN users_info as ui ON ui.id_login = ul.id
    """)
    keys = ["id","name", "cpf", "phone", "email", "birth_date", "position"]
    users_info = [dict(zip(keys, u)) for u in cursor.fetchall()]

    for user in users_info:
        user["birth_date"] = check_date(user.get("birth_date", ""), True)

    context["users_info"] = users_info
    finish_connection(connection, cursor)

    for category, msg in get_flashed_messages(with_categories=True):
        if category == "form_error" and isinstance(msg, dict):
            context[msg["field"]] = msg["message"]
            context.update(msg.get("context_update", {}))
        elif category == "success":
            context["success_message"] = msg
    return render_template("dashboard/users.html", context=context)

@dashboard_bp.route("/usuarios/excluir/<int:user_id>")
@login_required
def delete_user(user_id):
    return f"Usuário com ID {user_id}"

