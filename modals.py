import disnake
from disnake.ext import commands
from disnake import TextInputStyle
from verify import CheckAuthCode
from smtp import SendAuthCode
import variables
import re   

ROLES_CHANNEL_ID = variables.ROLES_CHANNEL_ID
BME_MEMBER_ROLE_ID = variables.BME_MEMBER_ROLE_ID
class VerificationFirstModal(disnake.ui.Modal):
    def __init__(self):
        components = [
            disnake.ui.TextInput(
                label="BME E-Mail Cím",
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
            await inter.response.send_message("A megadott E-Mail formátum nem megfelelő. Kötelező domain: `edu.bme.hu`", ephemeral=True)
            return
        await inter.response.defer(ephemeral=True)
        await SendAuthCode(bme_email)
        await inter.edit_original_response(f'Megadott email cím:\`**{bme_email}**\`(Ha a kód nem jelen meg az emaileid között, kérlek nézd meg a spam között, mielőtt segítséghez fordulsz!)\nKatt ide, hogy folytasd!', components=[
            disnake.ui.Button(label="Hitelesítés", style=disnake.ButtonStyle.success, custom_id="verify_code")
        ])
        return
    
def WelcomeEmbed(guildName):
    embed = disnake.Embed(title=f"Üdvözöljük a {guildName} szerveren!", description=f"Ne felejtsd el meglátogatni a <#{ROLES_CHANNEL_ID}> csatornát, hogy a rolejaidat átvedd, és a szabályzatokat elolvasd!", color=disnake.Color.dark_red())
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
            )
        ]
        super().__init__(title="Hitelesítés", components=components)

    async def callback(self, inter: disnake.ModalInteraction):
        auth_code = inter.text_values['auth_code']
        print(auth_code)
        correct_code = await CheckAuthCode(auth_code)
        if correct_code:
            await inter.user.send(embed=WelcomeEmbed("BME VIK Mérnökinformatika 2025 -"))
            bme_role = inter.guild.get_role(BME_MEMBER_ROLE_ID)
            await inter.user.add_roles(bme_role)
            await inter.response.send_message("Sikeres hitelesítés!", ephemeral=True)
        else:
            await inter.response.send_message("A megadott hitelesítő kód rossz.", ephemeral=True)
        return