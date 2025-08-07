import disnake
from disnake.ext import commands
from dotenv import load_dotenv
import os
import smtplib, ssl
from email_utils import smtp
from modules import variables
from modules.modals import VerificationFirstModal, VerificationSecondModal

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

async def IsInterestMessagePresent():
    last_message = await bot.get_channel(variables.INTEREST_CHANNEL_ID).history(limit = 1).flatten()
    is_empty = len(last_message) == 0
    if is_empty or last_message[0].author != bot.user:
        return False
    return True

def BuildVerificationEmbed():
    embed = disnake.Embed(title="Hitelesítés", description="Ahhoz hogy csatlakozhass a közösségünkhöz, kérlek hitelesítsd fiókod!\n\nAz üzenet alatti gombra kattintva, majd a [NEVED]@edu.bme.hu emailcímedet megadva kezdheted ezt meg. Emailcímet [ezen a linken](https://login.bme.hu/admin/username) tudsz igényelni, ha még esetleg nem tetted..\nA megerősítéshez az (Outlook-os) emailcímedre érkező kódra lesz szükséged.", color=disnake.Color.dark_red())
    return embed
def BuildInterestEmbed():
    embed = disnake.Embed(title="Érdeklődési kör választása", description="Az általános csevegésen kívül érdekel még más is? Az autók? A játékok? Esetleg a mémek? Itt ezekhez mind találhatsz egy külön csatornát.\n Ahhoz, hogy csatlakozhass, nem kell mást tenned csak az érdeklődésednek megfelelő gombokra kattintani!", color=disnake.Color.dark_red())
    return embed

def VerificationView():
    return

guild_invites = None

@bot.event
async def on_ready():
    is_vm_present = await IsVerificationMessagePresent()
    is_it_present = await IsInterestMessagePresent()
    if is_vm_present == False:
        VerificationEmbed = BuildVerificationEmbed()
        await bot.get_channel(variables.ENTRY_CHANNEL_ID).send(embed=VerificationEmbed, components=[
            disnake.ui.Button(label="Hitelesítés", style=disnake.ButtonStyle.success, custom_id="verify_email")
        ])
    if is_it_present == False:
        InterestEmbed = BuildInterestEmbed()
        await bot.get_channel(variables.INTEREST_CHANNEL_ID).send(embed=InterestEmbed, components=[
            disnake.ui.Button(label="Autók", style=disnake.ButtonStyle.success, custom_id="interest_car"),
            disnake.ui.Button(label="Játékok", style=disnake.ButtonStyle.success, custom_id="interest_game"),
            disnake.ui.Button(label="Shit-Post", style=disnake.ButtonStyle.success, custom_id="interest_shitpost"),
            disnake.ui.Button(label="Zenék", style=disnake.ButtonStyle.success, custom_id="interest_music"),
        ])
    guild_invites = await bot.get_guild(variables.GUILD_ID).invites()


@bot.event
async def on_member_join(member: disnake.Member):
    invites_before = guild_invites
    invites_after = await member.guild.invites()
    used_invite = None
    for before_invite in invites_before:
        for after_invite in invites_after:
            if before_invite.code == after_invite.code:
                if after_invite.uses > before_invite.uses:
                    used_invite = after_invite
                    break
    
    guild_invites = invites_after

    if used_invite:
        inviter = used_invite.inviter
        def BuildGuestApprovalEmbed():
            embed = disnake.Embed(title=f"A következő felhasználót ön hívta meg?", description=f"Felhasználónév: **{member.name}**({member.id})\n\nAbban az esetben vegye ezt az üzenetet figyelmen kívül, ha BME tagot hívott meg!")
            return embed
        embed = BuildGuestApprovalEmbed()
        await inviter.send(embed=embed, components=[
            disnake.ui.Button(label="Megerősítés", style=disnake.ButtonStyle.success, custom_id="guest_verify"),
            disnake.ui.Button(label="Elutasítás", style=disnake.ButtonStyle.success, custom_id="guest_deny")
        ])
        

@bot.listen("on_button_click")
async def verification_listener(interaction: disnake.MessageInteraction):

    if (interaction.component.custom_id == "verify_email"):
        await interaction.response.send_modal(VerificationFirstModal())

    if (interaction.component.custom_id == "verify_code"):
        bme_email = interaction.message.content.split('`')[1]
        await interaction.response.send_modal(VerificationSecondModal(bme_email))

    if (interaction.component.custom_id == "guest_verify"):
        userid = int(interaction.message.embeds[0].description.split("(")[1].split(')')[0])
        invitee = bot.get_guild(variables.GUILD_ID).get_member(userid)
        await invitee.add_roles(variables.NOT_BME_MEMBER_ROLE_ID)
        await interaction.response.send_message("Sikeresen megerősítve!")
        await invitee.send("A meghívó fél sikeresen megerősített!")

    if interaction.component.custom_id == "guest_deny":
        userid = int(interaction.message.embeds[0].description.split("(")[1].split(')')[0])
        invitee = bot.get_guild(variables.GUILD_ID).get_member(userid)
        await interaction.response.send_message("Sikeresen elutasítva!")
        await invitee.send("A meghívó fél elutasított.")
        await invitee.kick(reason="Declined by the inviter.")
    
    if (interaction.component.custom_id == "interest_car"):
        invitee = bot.get_guild(variables.GUILD_ID).get_member(userid)
        if invitee.get_role(variables.INTEREST_CAR_ROLE_ID) == None:
            await invitee.add_roles(variables.INTEREST_CAR_ROLE_ID)
        else:
            await invitee.remove_roles(variables.INTEREST_CAR_ROLE_ID)
    
    if (interaction.component.custom_id == "interest_game"):
        invitee = bot.get_guild(variables.GUILD_ID).get_member(userid)
        if invitee.get_role(variables.INTEREST_GAME_ROLE_ID) == None:
            await invitee.add_roles(variables.INTEREST_GAME_ROLE_ID)
        else:
            await invitee.remove_roles(variables.INTEREST_GAME_ROLE_ID)
    
    if (interaction.component.custom_id == "interest_shitpost"):
        invitee = bot.get_guild(variables.GUILD_ID).get_member(userid)
        if invitee.get_role(variables.INTEREST_SHITPOST_ROLE_ID) == None:
            await invitee.add_roles(variables.INTEREST_SHITPOST_ROLE_ID)
        else:
            await invitee.remove_roles(variables.INTEREST_SHITPOST_ROLE_ID)

    if (interaction.component.custom_id == "interest_music"):
        invitee = bot.get_guild(variables.GUILD_ID).get_member(userid)
        if invitee.get_role(variables.INTEREST_MUSIC_ROLE_ID) == None:
            await invitee.add_roles(variables.INTEREST_MUSIC_ROLE_ID)
        else:
            await invitee.remove_roles(variables.INTEREST_MUSIC_ROLE_ID)


bot.run(BOT_TOKEN)