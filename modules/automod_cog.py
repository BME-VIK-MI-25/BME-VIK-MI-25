from disnake.ext import commands, tasks
import disnake 
import modules.automod_definitions as automod_definitions
import modules.variables as variables
import modules.verify as verify
from datetime import datetime, timedelta, timezone

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
        records = await automod_definitions.GetBanExpiries()
        for record in records:
            if record.BanExpiry < datetime.now(timezone.utc): #timezone aware
                userid = record.userId
                
                await automod_definitions.DeleteBanExpiry(userid)

                guild = self.bot.get_guild(variables.GUILD_ID)
                member = guild.get_member(userid)
                role = guild.get_role(variables.BME_MEMBER_NOINVITE_ROLE_ID) 
                await member.remove_roles(role)
                
                role = guild.get_role(variables.BME_MEMBER_ROLE_ID) 
                await member.add_roles(role)
                
    @commands.slash_command(description="List invite banned users.")
    async def listbans(self, inter: disnake.ApplicationCommandInteraction):
        guild = self.bot.get_guild(variables.GUILD_ID)
        embed = disnake.Embed(
            title="Invite bannolt userek:",
            description="",
            color=disnake.Color.red()
        )  
        
        bans = await automod_definitions.GetBanExpiries()
        osszes = []
        for ban in bans:
            member = await self.bot.fetch_user(ban.userId)
            name = member.name
            embed.description += f'{member.name} {str(ban.BanExpiry.replace(tzinfo=None))[:-7]}\n'
        await inter.response.send_message(embed=embed)



def setup(bot):
    bot.add_cog(AutoMod(bot))