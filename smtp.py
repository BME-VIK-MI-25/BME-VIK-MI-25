from verify import CreateAuthCode
import smtplib, ssl
from dotenv import load_dotenv
from email.message import EmailMessage
import os

load_dotenv()

port = 465
context = ssl.create_default_context()
EMAIL = "bme@kadarmarcell.hu"
SMTP_PW = os.getenv("SMTP_PASSWORD")

async def SendAuthCode(to_email: str):
    auth_code = await CreateAuthCode(to_email)
    with smtplib.SMTP_SSL("mail.nethely.hu", port, context=context) as email_server:
        email_server.login(EMAIL, SMTP_PW)
        message = EmailMessage()
        message.set_content(f'A Discord szerveren történő hitelesítéshez szükséges kód: {auth_code}')
        message['Subject'] = "Discord szerver hitelesítés"
        message['From'] = EMAIL
        message['To'] = to_email
        message.set_charset('utf8')
        email_server.send_message(message)
    return