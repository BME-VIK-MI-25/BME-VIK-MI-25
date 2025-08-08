import disnake
from disnake.ext import commands
from dotenv import load_dotenv
import os
import smtplib, ssl
from email_utils import smtp
from modules import variables
from modules.modals import VerificationFirstModal, VerificationSecondModal, VerificationThirdModal, GuestConfirmationModal
from modules.verify import InsertInviteData, GetInviteData

intents = disnake.Intents.all()
bot = commands.InteractionBot(intents=intents, test_guilds=[1399074580727070761])

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
    embed = disnake.Embed(
        title="🔐 Hitelesítés szükséges",
        description="A szerver teljes eléréséhez előbb hitelesítened kell fiókod!",
        color=disnake.Color.dark_red()
    )

    embed.set_thumbnail(url=LOGO_VIK) #VIK logo

    embed.add_field(
        name="📧 1. Add meg az e-mail címed",
        value=(
            "Nyomj rá az üzenet alatti gombra, majd írd be a `[NEVED]@edu.bme.hu` e-mail címed.\n"
            "Nem tudod pontosan? Nézd meg a [címtárban](https://login.bme.hu/admin/username)!"
        ),
        inline=False
    )

    embed.add_field(
        name="📬 2. Ellenőrizd az e-mailjeidet",
        value="Erre az e-mail címedre az Outlook-on érzkezik egy kód, amit a következő lépésben kell megadnod.",
        inline=False
    )

    embed.set_footer(text="Az adataid biztonságban vannak. A hitelesítés kizárólag jogosultság-ellenőrzés céljából történik.")
    return embed

def BuildInterestEmbed():
    embed = disnake.Embed(title="🎯 Érdeklődési kör választása", description="Az általános csevegésen kívül érdekel még más is? 🚗 **Autók**? 🎮 **Játékok**? 🤣 **Mémek**? Itt ezekhez mind találhatsz egy külön csatornát.\n Ahhoz, hogy csatlakozhass, nem kell mást tenned csak az érdeklődésednek megfelelő gombokra kattintani!", color=disnake.Color.dark_red())
    embed.set_thumbnail(url=LOGO_HOBBY)
    return embed

def VerificationView():
    return



global guild_invites
guild_invites = None

@bot.event
async def on_ready():
    global guild_invites
    
    for filename in os.listdir("./modules"):
        if filename.endswith(".py") and filename.__contains__("cog"):
            bot.load_extension(f"modules.{filename[:-3]}")

    is_vm_present = await IsVerificationMessagePresent()
    is_it_present = await IsInterestMessagePresent()
    if is_vm_present == False:
        VerificationEmbed = BuildVerificationEmbed()
        await bot.get_channel(variables.ENTRY_CHANNEL_ID).send(embed=VerificationEmbed, components=[
            disnake.ui.Button(label="BME Tag", style=disnake.ButtonStyle.success, custom_id="verify_email"),
            disnake.ui.Button(label="Vendég", style=disnake.ButtonStyle.success, custom_id="verify_guest")
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
    global guild_invites
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
        InsertInviteData(member.id, inviter.id)
        

@bot.slash_command(description="Multiplies the number by a multiplier")
async def multiply(inter, number: int, multiplier: int = 7):
    await inter.response.send_message(number * multiplier)

@bot.listen("on_button_click")
async def verification_listener(interaction: disnake.MessageInteraction):

    match interaction.component.custom_id:
        case "verify_email":
            await interaction.response.send_modal(VerificationFirstModal())

        case "verify_guest":
            inviteeid = interaction.user.id
            invite_data = await GetInviteData(interaction.user.id)
            inviterid = invite_data.inviterid
            await interaction.response.send_modal(GuestConfirmationModal(inviterid, inviteeid))

        case "verify_code":
            bme_email = interaction.message.content.split('`')[1]
            await interaction.response.send_modal(VerificationSecondModal(bme_email))

        case "start_nickname_modal":
            await interaction.response.send_modal(VerificationThirdModal())

        case "guest_verify":
            userid = int(interaction.message.embeds[0].description.split("(")[1].split(')')[0])
            invitee = bot.get_guild(variables.GUILD_ID).get_member(userid)
            await invitee.add_roles(variables.NOT_BME_MEMBER_ROLE_ID)
            await interaction.response.send_message("Sikeresen megerősítve!")
            await invitee.send("A meghívó fél sikeresen megerősített!")

        case "guest_deny":
            userid = int(interaction.message.embeds[0].description.split("(")[1].split(')')[0])
            invitee = bot.get_guild(variables.GUILD_ID).get_member(userid)
            await interaction.response.send_message("Sikeresen elutasítva!")
            await invitee.send("A meghívó fél elutasított.")
            await invitee.kick(reason="Declined by the inviter.")

        case "interest_car":
            user = interaction.guild.get_member(interaction.user.id)
            role = interaction.guild.get_role(variables.INTEREST_CAR_ROLE_ID) 
            if user.get_role(variables.INTEREST_CAR_ROLE_ID) == None:
                await user.add_roles(role)
                await interaction.response.send_message("Megkaptad a kiválasztott rangod.", ephemeral=True)
            else:
                await user.remove_roles(role)
                await interaction.response.send_message("Elvettük az elvenni kívánt rangot.", ephemeral=True)

        case "interest_game":
            user = interaction.guild.get_member(interaction.user.id)
            role = interaction.guild.get_role(variables.INTEREST_GAME_ROLE_ID) 
            if user.get_role(variables.INTEREST_GAME_ROLE_ID) == None:
                await user.add_roles(role)
                await interaction.response.send_message("Megkaptad a kiválasztott rangod.", ephemeral=True)
            else:
                await user.remove_roles(role)
                await interaction.response.send_message("Elvettük az elvenni kívánt rangot.", ephemeral=True)

        case "interest_shitpost":
            user = interaction.guild.get_member(interaction.user.id)
            role = interaction.guild.get_role(variables.INTEREST_SHITPOST_ROLE_ID) 
            if user.get_role(variables.INTEREST_SHITPOST_ROLE_ID) == None:
                await user.add_roles(role)
                await interaction.response.send_message("Megkaptad a kiválasztott rangod.", ephemeral=True)
            else:
                await user.remove_roles(role)
                await interaction.response.send_message("Elvettük az elvenni kívánt rangot.", ephemeral=True)

        case "interest_music":
            user = interaction.guild.get_member(interaction.user.id)
            role = interaction.guild.get_role(variables.INTEREST_MUSIC_ROLE_ID)
            if user.get_role(variables.INTEREST_MUSIC_ROLE_ID) == None:
                await user.add_roles(role)
                await interaction.response.send_message("Megkaptad a kiválasztott rangod.", ephemeral=True)
            else:
                await user.remove_roles(role)
                await interaction.response.send_message("Elvettük az elvenni kívánt rangot.", ephemeral=True)



bot.run(BOT_TOKEN)