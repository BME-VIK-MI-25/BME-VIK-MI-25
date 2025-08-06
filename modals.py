import disnake
from disnake.ext import commands
from disnake import TextInputStyle

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
        await inter.response.send_message(f'Megadott email cím:{bme_email}\nKatt ide, hogy folytasd!', ephemeral=True, components=[
            disnake.ui.Button(label="Hitelesítés", style=disnake.ButtonStyle.success, custom_id="verify_code")
        ])
        return
    

class VerificationSecondModal(disnake.ui.Modal):
    def __init__(self, bme_email):
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
        return