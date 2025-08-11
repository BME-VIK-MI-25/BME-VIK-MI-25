import disnake
from disnake.ext import commands
from modules.variables import DYNAMIC_VOICE_CHANNEL_ID, GAMES_CATEGORY_ID, DYNAMIC_GAME_VOICE_CHANNEL_NAME

class DynamicVoiceChannel(commands.Cog):
    def __init__(self, bot: commands.InteractionBot):
        self.bot = bot
        return
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member: disnake.Member, before: disnake.VoiceState, after: disnake.VoiceState):
        left_channel = after.channel == None 
        if left_channel:
            user_count = len(before.channel.members)
            if before.channel.category.id != GAMES_CATEGORY_ID or user_count >= 1 or before.channel.id == DYNAMIC_VOICE_CHANNEL_ID:
                return
            
            await before.channel.delete()
            return
            
            
        if after.channel.id == DYNAMIC_VOICE_CHANNEL_ID:
            category = after.channel.category
            guild = member.guild
            channel_count = len(category.voice_channels)
            channel = await guild.create_voice_channel(f"{DYNAMIC_GAME_VOICE_CHANNEL_NAME}{channel_count}", category=category)
            await member.move_to(channel)

def setup(bot):
    bot.add_cog(DynamicVoiceChannel(bot))