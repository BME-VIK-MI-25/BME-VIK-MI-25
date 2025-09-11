from modules.verify import CreateAuthCode
import smtplib, ssl
from dotenv import load_dotenv
from email.message import EmailMessage
import os
from data.db import VerificationDict as authDict

load_dotenv()

port = 465
context = ssl.create_default_context()
EMAIL = "bme@kadarmarcell.hu"
SMTP_PW = os.getenv("SMTP_PASSWORD")

async def SendAuthCode(to_email: str):
    authCode = await CreateAuthCode(email=to_email, authDict=authDict)

    with smtplib.SMTP_SSL("mail.nethely.hu", port, context=context) as email_server:
        email_server.login(EMAIL, SMTP_PW)
        message = EmailMessage()
        html = f"""<html>
  <head>
    <meta charset="UTF-8">
    <meta name="color-scheme" content="light only">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,100..900;1,14..32,100..900&display=swap" rel="stylesheet">
  </head>

  <body style="margin: 0; padding: 0; background-color: #ffffff; bgcolor: #ffffff;">
    <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color: #ffffff; bgcolor: #ffffff;">
      <tr>
        <td align="center">
          <table width="600" cellpadding="0" cellspacing="0" border="0" style="background-color: #ffffff; bgcolor: #ffffff;">
            <tr>
              <td style="padding-left: 51px; font-family: 'Inter', sans-serif;">

                <img src="https://raw.githubusercontent.com/BME-VIK-MI-25/public-files/refs/heads/main/dclogo.png" style="margin-top: 45px; margin-bottom: 36px;"><br>

                <p style="margin: 0; font-size: 12px;">Kedves <b>Szaktársunk!</b></p><br>

                <p style="margin-top: 0; margin-bottom: 33px; width: 500px; font-size: 12px;">
                  Üdvözlünk a <b>BME VIK Mérnökinformatikusainak</b> discord szerverén. <br>
                  Még mielőtt teljes értékű taggá válhatnál, add meg a <b>discord botunknak</b> az alábbi hitelesítőkódot:
                </p>

                <div style="background-color: black; width: 102px; height: 28px; border-radius: 20px; display: flex; justify-content: center; align-items: center; margin-bottom: 33px; margin-left: 199px; ">
                  <p style="color: #ffffff; font-size: 13px; font-weight: bold; margin: 0;">{authCode}</p>
                </div>

                <p style="width: 500px; font-size: 12px; margin-top: 0;">
                  Minden fontos információt megtalálsz a szobákban. Az éppen aktuális időpontokról pedig, az <b>események</b>-nél tájékozódhatsz.
                  Ha esetleg így sem találnál meg egy információt, ne habozz, kérdezd meg a többieket!
                </p>
                <br>
                <p style="font-size: 12px; margin-top: 0;">Kellemes időtöltést, és hatékony tanulást kívánunk! 😁</p>

              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
  </body>
</html>
"""
        message['Subject'] = "BME VIK Mérnökinformatika 2025 - Hitelesítés"
        message['From'] = EMAIL
        message['To'] = to_email
        message.add_alternative(html, subtype='html')
        email_server.send_message(message)
    return