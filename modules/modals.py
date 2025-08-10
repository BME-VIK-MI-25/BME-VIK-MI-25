import disnake
from disnake.ext import commands
from disnake import TextInputStyle
from modules.verify import CheckAuthCode
from email_utils.smtp import SendAuthCode
import modules.variables as variables
import re   
import modules.verify
import logging
import modules.logging_config as logging_config

ROLES_CHANNEL_ID = variables.ROLES_CHANNEL_ID
BME_MEMBER_ROLE_ID = variables.BME_MEMBER_ROLE_ID

def BuildGuestConfirmEmbed(interaction):
    embed = disnake.Embed(title=f"Ezt a felhasználót te hívtad meg?", description=f"Felhasználónév: **{interaction.user.name}** ({interaction.user.id})\n\nVedd ezt az üzenetet figyelmen kívül, ha **BME** tagot hívtál meg!", color=disnake.Color.dark_red())
    return embed


class VerificationFirstModal(disnake.ui.Modal):
    def __init__(self):
        components = [
            disnake.ui.TextInput(
                label="BME e-mail cím",
                placeholder="XYZ@edu.bme.hu",
                custom_id="bme_email",
                style=TextInputStyle.short,
                max_length=50
            )
        ]
        super().__init__(title="Hitelesítés", components=components)

    async def callback(self, inter: disnake.ModalInteraction):
        bme_email = inter.text_values['bme_email']
        if re.match(".*@edu\.bme\.hu", bme_email) == None:
            await inter.response.send_message("A megadott e-mail formátum nem megfelelő. Kötelező domain: `edu.bme.hu`", ephemeral=True)
            return
        await inter.response.defer(ephemeral=True)
        await SendAuthCode(bme_email)
        await inter.edit_original_response(f'Megadott e-mail cím:\`**{bme_email}**\`(Ha a kód nem jelenik meg az e-mailjeid között, nézd meg a spam-ek között, mielőtt segítséghez fordulsz!)\nKatt ide, hogy folytasd!', components=[
            disnake.ui.Button(label="Hitelesítés", style=disnake.ButtonStyle.success, custom_id="verify_code")
        ])
        return
    
def WelcomeEmbed(guildName):
    embed = disnake.Embed(title=f"Üdvözlünk a {guildName} szerveren!", description=f"Ne felejtsd el meglátogatni a <#{ROLES_CHANNEL_ID}> csatornát, hogy a rolejaidat átvedd!", color=disnake.Color.dark_red())
    return embed

def BuildBmeEmailEmbed(bme_email: str, mention):
    embed = disnake.Embed(title="EMAIL LOG")
    embed.add_field(name="Felhasználó(említve)", value=f"{mention}")
    embed.add_field(name="Email cím", value=f"{bme_email}")
    return embed

class VerificationSecondModal(disnake.ui.Modal):
    def __init__(self, bme_email):
        self.bme_email = bme_email
        components = [
            disnake.ui.TextInput(
                label="Hitelesítő kód",
                placeholder="XXXXXXXXXX",
                custom_id="auth_code",
                style=TextInputStyle.short,
                max_length=10
            ),
            disnake.ui.TextInput(
                label="Teljes név megadása",
                placeholder="Vicc Elek",
                custom_id="nickname",
                style=disnake.TextInputStyle.short,
                max_length=32,
            )
        ]
        super().__init__(title="Hitelesítés", components=components)

    async def callback(self, inter: disnake.ModalInteraction):
        await inter.response.defer(ephemeral=True)
        # Hitelesítő kód
        auth_code = inter.text_values['auth_code']
        print(auth_code)
        try:
            correct_code = await CheckAuthCode(auth_code)
        except:
            await inter.edit_original_response("A megadott hitelesítési kód hibás, vagy hiányos!")
        if correct_code:
            await inter.user.send(embed=WelcomeEmbed("BME VIK Mérnökinformatika 2025 -"))
            bme_role = inter.guild.get_role(BME_MEMBER_ROLE_ID)
            await inter.user.add_roles(bme_role)
            self.bme_email = self.bme_email.replace('\\', '')
            await inter.guild.get_channel(variables.BME_EMAIL_LOG_CHANNEL_ID).send(embed = BuildBmeEmailEmbed(self.bme_email, inter.user.mention))

            # Teljes név
            new_nick = inter.text_values["nickname"]
            try:
                await inter.user.edit(nick=new_nick)
                await inter.edit_original_response(f"A beceneved a szerveren az általad megadott névre módosítottuk. Érezd jól magad a továbbiakban is **{new_nick}**!")

            except disnake.Forbidden:
                await inter.edit_original_response(f"Sajnos nincs jogosultságom megváltoztatni a nevedet. Valami balul sült el, kérlek jelezd a fejlesztőknek!")
            except disnake.HTTPException as e:
                await inter.edit_original_response(f"Hiba történt! Keresd fel a fejlesztőket!") 
                logging.error(f'Nickname change error for: {inter.user.name}\n{e}')
        else:
            await inter.edit_original_response("A megadott hitelesítő kód rossz.")
        return