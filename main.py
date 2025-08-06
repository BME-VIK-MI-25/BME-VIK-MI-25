import disnake
from disnake.ext import commands
from dotenv import load_dotenv
import os
import smtplib, ssl
import smtp

bot = commands.InteractionBot()

load_dotenv()

BOT_TOKEN = os.getenv("TOKEN")

bot.run(BOT_TOKEN)