from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib, os

def send_email(email_to_send, subject, email_template):

    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    EMAIL = os.getenv("EMAIL")
    SENHA = os.getenv("SENHA_EMAIL")

    msg = MIMEMultipart("alternative")
    msg["From"] = EMAIL
    msg["To"] = email_to_send
    msg["Subject"] = subject

    msg.attach(MIMEText(email_template, 'html'))
    print('entrou na função')

    try:
        # Envio do email ao usuário
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL, SENHA)
            server.sendmail(EMAIL, msg["To"], msg.as_string())
            print('enviou')
    except:
        print('n enviou')
        raise