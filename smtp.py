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
        html = f"""<html>
                            <head></head>
                            <body>
                            <center>
                                <img src="https://play-lh.googleusercontent.com/074LK6vDEKUreS4u50Yf3DiDyE0Mgs4yVAe6zmkl2vdWCRVIbAboAEcToZZHHi-Um4SD" width="392px" height="392px"/>
                            <h2>A szerveren való hitelesítéshez szükséges kód:<br><span style="background-color: rgb(20, 20, 20); padding: 5px;"><b>{auth_code}</b></span></h2>
                            </center>
                            </body>
                            </html>"""
        message['Subject'] = "BME VIK Mérnökinformatika 2025 - Hitelesítés"
        message['From'] = EMAIL
        message['To'] = to_email
        message.add_alternative(html, subtype='html')
        email_server.send_message(message)
    return