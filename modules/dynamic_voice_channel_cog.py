import disnake
from disnake.ext import commands
from modules.variables import DYNAMIC_VOICE_CHANNEL_ID, GAMES_CATEGORY_ID

class DynamicVoiceChannel(commands.Cog):
    def __init__(self, bot: commands.InteractionBot):
        self.bot = bot
        return
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member: disnake.Member, before: disnake.VoiceState, after: disnake.VoiceState):
        
        joined_channel = after.channel.id if after.channel else None
        category = after.channel.category if after.channel else before.channel.category

        if joined_channel != DYNAMIC_VOICE_CHANNEL_ID:
            user_count = len(after.channel.members if after.channel else before.channel.members)
            if category.id != GAMES_CATEGORY_ID:
                return
            if user_count >= 1:
                return
            
            await before.channel.delete()
            return
            
            

        guild = member.guild

        channel = await guild.create_voice_channel("Game Channel", category=category)
        await member.move_to(channel)

def setup(bot):
    bot.add_cog(DynamicVoiceChannel(bot))