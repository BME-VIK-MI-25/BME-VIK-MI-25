import disnake
from disnake.ext import commands
from disnake import TextInputStyle
from modules.verify import CheckAuthCode
from email_utils.smtp import SendAuthCode
import modules.variables as variables
import re   
import modules.verify

ROLES_CHANNEL_ID = variables.ROLES_CHANNEL_ID
BME_MEMBER_ROLE_ID = variables.BME_MEMBER_ROLE_ID
class VerificationFirstModal(disnake.ui.Modal):
    def __init__(self):
        components = [
            disnake.ui.TextInput(
                label="BME Email Cím",
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
            await inter.response.send_message("A megadott email formátum nem megfelelő. Kötelező domain: `edu.bme.hu`", ephemeral=True)
            return
        await inter.response.defer(ephemeral=True)
        await SendAuthCode(bme_email)
        await inter.edit_original_response(f'Megadott email cím:\`**{bme_email}**\`(Ha a kód nem jelenik meg az emailjeid között, kérlek nézd meg a spam-ek között, mielőtt segítséghez fordulsz!)\nKatt ide, hogy folytasd!', components=[
            disnake.ui.Button(label="Hitelesítés", style=disnake.ButtonStyle.success, custom_id="verify_code")
        ])
        return
    
def WelcomeEmbed(guildName):
    embed = disnake.Embed(title=f"Üdvözlünk a {guildName} szerveren!", description=f"Ne felejtsd el meglátogatni a <#{ROLES_CHANNEL_ID}> csatornát, hogy a rolejaidat átvedd!", color=disnake.Color.dark_red())
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
        try:
            correct_code = await CheckAuthCode(auth_code)
        except:
            await inter.response.send_message("A megadott hitelesítési kód hibás, vagy hiányos!", ephemeral=True)
        if correct_code:
            await inter.user.send(embed=WelcomeEmbed("BME VIK Mérnökinformatika 2025 -"))
            bme_role = inter.guild.get_role(BME_MEMBER_ROLE_ID)
            await inter.user.add_roles(bme_role)
            await inter.response.send_message("Sikeres hitelesítés! Kérlek add meg a beceneved", components=[
            disnake.ui.Button(label="Becenév megadása", style=disnake.ButtonStyle.success, custom_id="start_nickname_modal")], ephemeral=True)
        else:
            await inter.response.send_message("A megadott hitelesítő kód rossz.", ephemeral=True)
        return
    
class VerificationThirdModal(disnake.ui.Modal): # set nickname
    def __init__(self):
        components = [
            disnake.ui.TextInput(
                label="Becenév megadása",
                placeholder="Becenév",
                custom_id="nickname",
                style=disnake.TextInputStyle.short,
                max_length=32,
            )
        ]
        super().__init__(title="Becenév beállítása", components=components, custom_id="nickname_modal")
        
    async def callback(self, interaction: disnake.ModalInteraction):
        new_nick = interaction.text_values["nickname"]
        try:
            await interaction.author.edit(nick=new_nick)
            await interaction.response.send_message(f"A becenevedet a szerveren az általad megadott névre módosítottuk. Érezd jól magad a továbbiakban is **{new_nick}**!", ephemeral=True)
            await modules.verify.RemoveInviteDataOnSuccessfulAuth(interaction.user.id)
        except disnake.Forbidden:
            await interaction.response.send_message(f"Sajnos nincs jogosultságom megváltoztatni a nevedet. Valami balul sült el, kérlek jelezd a fejlesztőknek!", ephemeral=True)
        except disnake.HTTPException as e:
            await interaction.response.send_message(f"O-ó... Nagy hiba van: {e}", ephemeral=True) 

class GuestConfirmationModal(disnake.ui.Modal):
    def __init__(self, inviterId, inviteeId):
        self.inviterId = inviterId
        self.inviteeId = inviteeId
        
        components = [
            disnake.ui.TextInput(
                label="Megerősítés",
                placeholder="'IGEN' vagy 'NEM'",
                custom_id="confirmation",
                style=TextInputStyle.short,
                max_length=4
            )
        ]
        super().__init__(title="Megerősítés", components=components)

    async def callback(self, interaction: disnake.ModalInteraction):
        confirmation_value = interaction.text_values['confirmation'].upper()

        match confirmation_value:
            case 'IGEN':
                embed = embed = disnake.Embed(title=f"Ezt a felhasználót te hívtad meg?", description=f"Felhasználónév: **{interaction.user.name}** ({interaction.user.id})\n\nVedd ezt az üzenetet figyelmen kívül, ha **BME** tagot hívtál meg!", color=disnake.Color.dark_red())
                
                inviter = interaction.guild.get_member(self.inviterId)
                await inviter.send(embed=embed, components=[
                    disnake.ui.Button(label="Megerősítés", style=disnake.ButtonStyle.success, custom_id="guest_verify"),
                    disnake.ui.Button(label="Elutasítás", style=disnake.ButtonStyle.success, custom_id="guest_deny")
                ])

                await interaction.response.send_message("Sikeres választás! Aki meghívott, kapott egy megerősítő üzenetet, amint megerősítenek, megkapod a szerverhez való hozzáférést!", ephemeral=True)
                modules.verify.RemoveInviteData(self.inviteeId, self.inviterId)
            case 'NEM':
                await interaction.response.send_message("Sikeres választás!", ephemeral=True)
