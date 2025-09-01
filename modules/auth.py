import bcrypt, uuid, smtplib, random
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
        SMTP_SERVER = "smtp.gmail.com"
        SMTP_PORT = 587
        EMAIL = "ong.sos4patas0@gmail.com"
        SENHA = "knyq kmzb lwey krio"
        recovery_code = str(random.randint(100000, 999999)) 
        reset_email = request.form.get("reset_email", "").strip()

        cursor.execute('SELECT login FROM users_login WHERE login = ?', (reset_email,))
        reset_email = cursor.fetchone()
        
        if reset_email is not None:
            msg = MIMEMultipart("alternative")
            msg["From"] = EMAIL
            msg["To"] = reset_email[0]
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

            # Envio
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(EMAIL, SENHA)
                server.sendmail(EMAIL, msg["To"], msg.as_string())

            print("Email HTML enviado com sucesso!")

            session['recovery_code'] = bcrypt.hashpw(recovery_code.encode(), bcrypt.gensalt()).decode()
            return redirect(url_for('verify_code'))
        else:
            context['error'] = 'Erro ao recuperar a senha'
            return render_template('reset_password.html', context=context)

    return render_template('reset_password.html', context=context)