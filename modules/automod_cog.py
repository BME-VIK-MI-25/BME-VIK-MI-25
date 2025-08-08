from disnake.ext import commands, tasks
import disnake 
import modules.automod_definitions as automod_definitions
import modules.variables as variables
import modules.verify as verify
from datetime import datetime, timedelta

class AutoMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.AutoCheckInviteBans.start()
    
    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message):
        automod_result = await automod_definitions.CheckBannedWord(message, message.author.id)
        if automod_result == False:
            return
        await message.delete()

        BannedWordCount = await automod_definitions.GetBannedWordCount(message.author.id)
        if BannedWordCount >= variables.BannedWordCountThreshold:
            await message.guild.ban(message.author, reason="Bannolt szavak használata")
            inviter = await verify.GetInviteData(message.author.id)

            role = message.guild.get_role(variables.BME_MEMBER_NOINVITE_ROLE_ID) 
            await inviter.add_roles(role)

            role = message.guild.get_role(variables.BME_MEMBER_ROLE_ID) 
            await inviter.remove_roles(role)
            await automod_definitions.UpdateBanExpiry(message.author.id,datetime.now()+timedelta(days=7))
        # Handle banned word count checking, invitee and invite bans
    
    @tasks.loop(seconds=180) # Öt vagy egy perc? Feri: Három
    async def AutoCheckInviteBans(self):
        for record in await automod_definitions.GetBanExpiries():
            if record.BanExpiry < datetime.now():
                userid = record.userId
                guild = self.bot.get_guild(variables.GUILD_ID)
                member = guild.get_member(userid)
                role = guild.get_role(variables.BME_MEMBER_NOINVITE_ROLE_ID) 
                await member.remove_roles(role)
                
                role = guild.get_role(variables.BME_MEMBER_ROLE_ID) 
                await member.add_roles(role)
        
    @commands.slash_command()
    @commands.has_permissions(manage_roles=True)
    async def banword(self, inter: disnake. ApplicationCommandInteraction, word: str):
        await automod_definitions.InsertBannedWord(word)
        await inter.response.send_message(f"{word} sikeresen tiltva.", ephemeral=True)

    @commands.slash_command()
    @commands.has_permissions(manage_roles=True)
    async def banwords(self, inter: disnake. ApplicationCommandInteraction, words: str=commands.Param(description="Vesszővel(,) válazd el!")):
        await automod_definitions.InsertBannedWord(words)
        await inter.response.send_message(f"{words} sikeresen tiltva.", ephemeral=True)
                






def setup(bot):
    bot.add_cog(AutoMod(bot))