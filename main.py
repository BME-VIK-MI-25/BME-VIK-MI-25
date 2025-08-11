import disnake
from disnake.ext import commands
from dotenv import load_dotenv
import os
from modules import variables
from modules.modals import VerificationFirstModal, VerificationSecondModal
from modules.verify import InsertInviteData, GetInviteData
from modules.log import log_message

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

    embed.set_thumbnail(url=variables.LOGO_VIK) #VIK logo

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
    embed.set_thumbnail(url=variables.LOGO_HOBBY)
    return embed

def VerificationView():
    return



global guild_invites
guild_invites = None

@bot.event
async def on_ready():
    global guild_invites
    await log_message(bot, "info","Bot starting up...")
    for filename in os.listdir("./modules"):
        if filename.endswith(".py") and filename.__contains__("cog"):
            bot.load_extension(f"modules.{filename[:-3]}")
"""
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
        await InsertInviteData(member.id, inviter.id)


@bot.slash_command(description="Multiplies the number by a multiplier")
async def multiply(inter, number: int, multiplier: int = 7):
    await inter.response.send_message(number * multiplier)

def BuildGuestConfirmEmbed(interaction):
    embed = disnake.Embed(title=f"Ezt a felhasználót te hívtad meg?", description=f"Felhasználónév: **{interaction.user.name}** ({interaction.user.id})\n\nVedd ezt az üzenetet figyelmen kívül, ha **BME** tagot hívtál meg!", color=disnake.Color.dark_red())
    return embed

@bot.listen("on_button_click")
async def verification_listener(interaction: disnake.MessageInteraction):
    CUSTOM_ID = interaction.component.custom_id

    match CUSTOM_ID:
        case "verify_email":
            await interaction.response.send_modal(VerificationFirstModal())

        case "verify_guest":
            inviteeid = interaction.user.id
            invite_data = await GetInviteData(interaction.user.id)
            if invite_data == None:
                await interaction.response.send_message("A felhasználó aki meghívott nem szerepel az adatbázisban. Kérjük, kérj segítséget vagy használd BME-s emailed a hitelesítéshez.", ephemeral=True)
                return
            inviterid = invite_data.inviterid
            embed = BuildGuestConfirmEmbed(interaction)
                
            inviter = interaction.guild.get_member(inviterid)
            await inviter.send(embed=embed, components=[
                disnake.ui.Button(label="Megerősítés", style=disnake.ButtonStyle.success, custom_id="guest_verify"),
                disnake.ui.Button(label="Elutasítás", style=disnake.ButtonStyle.success, custom_id="guest_deny")
            ])

            await interaction.response.send_message("Sikeres választás! Aki meghívott, kapott egy megerősítő üzenetet, amint megerősítenek, megkapod a szerverhez való hozzáférést!", ephemeral=True)

        case "verify_code":
            bme_email = interaction.message.content.split('`')[1]
            await interaction.response.send_modal(VerificationSecondModal(bme_email))

        case "guest_verify":
            userid = int(interaction.message.embeds[0].description.split("(")[1].split(')')[0])
            invitee = bot.get_guild(variables.GUILD_ID).get_member(userid)
            guestrole = bot.get_guild(variables.GUILD_ID).get_role(variables.NOT_BME_MEMBER_ROLE_ID)
            await invitee.add_roles(guestrole)
            await interaction.response.send_message("Sikeresen megerősítve!")
            await invitee.send("A meghívó fél sikeresen megerősített!")

        case "guest_deny":
            userid = int(interaction.message.embeds[0].description.split("(")[1].split(')')[0])
            invitee = bot.get_guild(variables.GUILD_ID).get_member(userid)
            await interaction.response.send_message("Sikeresen elutasítva!")
            await invitee.send("A meghívó fél elutasított.")
            await invitee.kick(reason="Declined by the inviter.")

        case _:
            if CUSTOM_ID.__contains__("interest") or CUSTOM_ID.__contains__("role"):
                user = interaction.guild.get_member(interaction.user.id)
                role_id = variables.CUSTOMID_ROLE_PAIRS[CUSTOM_ID]
                role = interaction.guild.get_role(role_id) 
                if user.get_role(role_id) == None:
                    await user.add_roles(role)
                    await interaction.response.send_message("Megkaptad a kiválasztott rangod.", ephemeral=True)
                else:
                    await user.remove_roles(role)
                    await interaction.response.send_message("Elvettük az elvenni kívánt rangot.", ephemeral=True)
"""

bot.run(BOT_TOKEN)