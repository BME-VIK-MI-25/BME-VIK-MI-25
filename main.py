import disnake
from disnake.ext import commands
from dotenv import load_dotenv
import os
import smtplib, ssl
import smtp
import variables
from modals import VerificationFirstModal, VerificationSecondModal

intents = disnake.Intents.all()
bot = commands.InteractionBot(intents=intents)

load_dotenv()

BOT_TOKEN = os.getenv("TOKEN")

async def IsVerificationMessagePresent():
    last_message = await bot.get_channel(variables.ENTRY_CHANNEL_ID).history(limit = 1).flatten()
    is_empty = len(last_message) == 0
    if is_empty or last_message[0].author != bot.user:
        return False
    return True

def BuildVerificationEmbed():
    embed = disnake.Embed(title="Hitelesítés", description="Hogy hozzáférést szerezz a szerver többi részéhez, kérlek hitelesítsd fiókod!\n\nHogy ezt megtedd, az üzenet alatt lévő gombra nyomj rá, majd a [NEVED].edu.bme.hu emailcímedet add meg.\nEzt követően erre az email címre(Outlook) kapsz egy kódot, amelyet meg kell adnod.", color=disnake.Color.dark_red())
    return embed

def VerificationView():
    return

@bot.event
async def on_ready():
    is_vm_present = await IsVerificationMessagePresent()
    if is_vm_present == False:
        VerificationEmbed = BuildVerificationEmbed()
        await bot.get_channel(variables.ENTRY_CHANNEL_ID).send(embed=VerificationEmbed, components=[
            disnake.ui.Button(label="Hitelesítés", style=disnake.ButtonStyle.success, custom_id="verify_email")
        ])

@bot.listen("on_button_click")
async def verification_listener(interaction: disnake.MessageInteraction):

    if (interaction.component.custom_id == "verify_email"):
        await interaction.response.send_modal(VerificationFirstModal())

    if (interaction.component.custom_id == "verify_code"):
        bme_email = interaction.message.content.split(':')[1].split('\n')[0]
        await interaction.response.send_modal(VerificationSecondModal(bme_email))

bot.run(BOT_TOKEN)