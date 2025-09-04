import bcrypt, uuid, smtplib, random, os, datetime
from modules.manager_database import connect_to_db, finish_connection
from flask import request, redirect, url_for, session, flash, render_template
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from modules.utils.validations import password_validator


# ===============================
# Função responsável por registrar um novo usuário
# ===============================
def user_register():
    connection, cursor = connect_to_db()
    signup_login = request.form.get("signup-login", "").strip()
    signup_password = bcrypt.hashpw(
        request.form.get("signup-password", "").strip().encode(),
        bcrypt.gensalt()
    )

    try:
        # Inserção do novo usuário no banco de dados
        cursor.execute(
            'INSERT INTO users_login (login, password) VALUES (?, ?)',
            (signup_login, signup_password,)
        )
        connection.commit()
        finish_connection(connection, cursor)

        flash("Conta criada com sucesso!", "success")
        # Redireciona para login após criação
        return redirect(url_for("login"))

    except:
        # erro ao criar conta
        flash("Não foi possivel criar sua conta!")


# ===============================
# Função responsável por autenticar o usuário
# ===============================
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

        # Validação da senha
        if bcrypt.checkpw(login_password, hashed_password):
            # Geração de novo token de sessão
            session["session_token"] = str(uuid.uuid4())
            session['user_login'] = login

            # Atualiza token no banco para login único
            cursor.execute(
                'UPDATE users_login SET session_token = ? WHERE login = ?',
                (session.get('session_token', ''), login,)
            )
            connection.commit()

            finish_connection(connection, cursor)
            flash("Sua conta foi criada com sucesso!", "success")
            return redirect(url_for("dashboard"))

    # Se falhar login, encerra conexão e retorna erro
    finish_connection(connection, cursor)
    context['error'] = 'Usuário ou Senha inválido'
    return render_template("login.html", context=context)


# ===============================
# Função responsável por envio do código de recuperação
# ===============================
def send_code():
    context = {'title': 'Recuperação de Senha'}
    connection, cursor = connect_to_db()

    if request.method == "POST":
        now = datetime.datetime.now()

        # Configurações de e-mail
        SMTP_SERVER = "smtp.gmail.com"
        SMTP_PORT = 587
        EMAIL = os.getenv("EMAIL")
        SENHA = os.getenv("SENHA_EMAIL")

        # Gera código aleatório de 6 dígitos
        recovery_code = str(random.randint(100000, 999999))
        reset_email = request.form.get("reset_email", "").strip()

        # Consulta usuário e códigos ativos
        cursor.execute('''SELECT ul.id, ul.login, pr.id
                          FROM users_login as ul 
                          LEFT JOIN passwords_resets as pr 
                          ON pr.id_login = ul.id AND pr.used = 0 AND expired_at > ?
                          WHERE login = ?''',
                          (now.strftime("%Y-%m-%d %H:%M:%S"), reset_email))

        result_query = cursor.fetchone() or (None, None, None)
        id_login, email_recovery, id_password_reset = result_query

        # Se não existe código válido
        if id_password_reset is None:
            if (email_recovery and EMAIL and SENHA) is not None:
                msg = MIMEMultipart("alternative")
                msg["From"] = EMAIL
                msg["To"] = email_recovery
                msg["Subject"] = "Redefinição de Senha"

                html = f"""
                <html>
                <body style="font-family: Arial, sans-serif; text-align: center; background: #f4f6f8; padding: 20px;">
                    <div style="max-width: 500px; margin: auto; background: #ffffff; padding: 30px; border-radius: 8px; box-shadow: 0 2px 6px rgba(0,0,0,0.1);">
                        <h2 style="color: #2c3e50;">Olá, Marcus!</h2>
                        <p style="font-size: 16px; color: #555;">Você solicitou a recuperação de senha.</p>
                        <p style="font-size: 16px; color: #555;">Digite o código abaixo para continuar:</p>
                        <div style="margin: 25px 0; text-align: center;">
                            {''.join([f'<span style="display:inline-block; width:45px; height:55px; line-height:55px; margin:5px; border:2px solid #3498db; border-radius:6px; font-size:22px; font-weight:bold; color:#2c3e50; text-align:center;">{digit}</span>' for digit in recovery_code])}
                        </div>
                        <p style="font-size: 14px; color: #777;">Se você não fez essa solicitação, ignore este email.</p>
                    </div>
                </body>
                </html>
                """
                msg.attach(MIMEText(html, "html"))

                try:
                    # Envio do email ao usuário
                    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                        server.starttls()
                        server.login(EMAIL, SENHA)
                        server.sendmail(EMAIL, msg["To"], msg.as_string())

                    # Salva hash do código no banco
                    recovery_code = bcrypt.hashpw(recovery_code.encode(),bcrypt.gensalt()).decode()

                    cursor.execute(
                        'INSERT INTO passwords_resets (id_login, code_hash, expired_at, used) VALUES (?, ?, ?, ?)',
                        (id_login, recovery_code,
                         (now + datetime.timedelta(minutes=10)).strftime("%Y-%m-%d %H:%M:%S"),
                         False)
                    )
                    id_password_reset = cursor.lastrowid

                    connection.commit()
                    session['id_password_reset'] = id_password_reset
                    finish_connection(connection, cursor)

                    return redirect(url_for('verify_code'))

                except:
                    context['error'] = 'Erro ao enviar o email'
            else:
                context['error'] = 'Erro ao recuperar a senha'
        else:
            # Já existe código válido
            session['id_password_reset'] = id_password_reset
            session["valid_code"] = True
            return redirect(url_for('verify_code'))

    finish_connection(connection, cursor)
    return render_template('recovery_password.html', context=context)


# ===============================
# Função responsável por redefinir a senha
# ===============================
def reset_password():
    context = {'title': 'Redefinir Senha'}
    connection, cursor = connect_to_db()

    if request.method == 'POST':
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('password-confirm', '').strip()

        if password == confirm_password:
            if password_validator(password):
                password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
                cursor.execute(
                    'UPDATE users_login SET password = ? WHERE id = ?',
                    (password, session.pop('confirmed_user_id'))
                )
                connection.commit()
                finish_connection(connection, cursor)
                return redirect(url_for('login'))
            else:
                context['error'] = 'Senha inválida'
        else:
            context['error'] = 'As senhas não são iguais'

    return render_template('reset_password.html', context=context)