from disnake.ext import commands
import disnake 
import modules.automod_definitions as automod_definitions

class AutoMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_message(message: disnake.Message):
        automod_result = automod_definitions.CheckBannedWord(message)
        if automod_result == False:
            return
        await message.delete()
        # Handle banned word count checking, invitee and invite bans