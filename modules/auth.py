import bcrypt, uuid, smtplib, random, os, datetime
from modules.manager_database import connect_to_db, finish_connection
from flask import request, redirect, url_for, session, flash, render_template
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def user_register():
    connection, cursor = connect_to_db()
    signup_login = request.form.get("signup-login", "").strip()
    signup_password = bcrypt.hashpw(request.form.get("signup-password", "").strip().encode(), bcrypt.gensalt())
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
    context['error'] = 'Usuário ou Senha inválido'
    return render_template("login.html", context=context)

def reset_password():
    context = {}
    connection, cursor = connect_to_db()
    if request.method == "POST":
        now = datetime.datetime.now()
        SMTP_SERVER = "smtp.gmail.com"
        SMTP_PORT = 587
        EMAIL = os.getenv("EMAIL")
        SENHA = os.getenv("SENHA_EMAIL")
        recovery_code = str(random.randint(100000, 999999)) 
        reset_email = request.form.get("reset_email", "").strip()

        cursor.execute('''SELECT ul.id, ul.login, pr.id
                          FROM users_login as ul 
                          LEFT JOIN passwords_resets as pr ON pr.id_login = ul.id AND pr.used = 0 AND expired_at > ?
                          WHERE login = ?''', (now.strftime("%Y-%m-%d %H:%M:%S"), reset_email))
        
        result_query = cursor.fetchone() or (None, None, None)
        id_login, email_recovery, id_password_reset = result_query
        
        if id_password_reset is None:
            if (email_recovery and EMAIL and SENHA) is not None:
                msg = MIMEMultipart("alternative")
                msg["From"] = EMAIL
                msg["To"] = email_recovery
                msg["Subject"] = "Teste de Email HTML"
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
                    # Envio do Email ao USuario
                    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                        server.starttls()
                        server.login(EMAIL, SENHA)
                        server.sendmail(EMAIL, msg["To"], msg.as_string())

                    print("Email HTML enviado com sucesso!")

                    recovery_code = bcrypt.hashpw(recovery_code.encode(), bcrypt.gensalt()).decode()

                    cursor.execute('INSERT INTO passwords_resets (id_login, code_hash, expired_at, used) VALUES (?, ?, ?, ?)', (id_login,recovery_code, (now + datetime.timedelta(minutes=10)).strftime("%Y-%m-%d %H:%M:%S"), False))
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
            session['id_password_reset'] = id_password_reset
            session["valid_code"] = True
            return redirect(url_for('verify_code'))
            
    finish_connection(connection, cursor)
    return render_template('reset_password.html', context=context)