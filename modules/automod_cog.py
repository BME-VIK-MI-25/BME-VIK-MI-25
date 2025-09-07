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
        try:
            await message.delete()
        except disnake.NotFound:
            print("Az üzenetet már törölték.")
        except disnake.Forbidden:
            print("Nincs jogosultságom törölni az üzenetet.")

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
            if record.inviteBanExpiry < datetime.now(timezone.utc): #timezone aware

                userid = record.userId
                
                await automod_definitions.DeleteBanExpiry(userid)

                guild = self.bot.get_guild(variables.GUILD_ID)
                member = guild.get_member(userid)
                role = guild.get_role(variables.BME_MEMBER_NOINVITE_ROLE_ID) 
                await member.remove_roles(role)
                
                role = guild.get_role(variables.BME_MEMBER_ROLE_ID) 
                await member.add_roles(role)
        
    @commands.slash_command()
    @commands.has_permissions(manage_roles=True)
    async def banword(self, inter: disnake.ApplicationCommandInteraction, word: str):
        await automod_definitions.InsertBannedWord(word)
        await inter.response.send_message(f"{word} sikeresen tiltva.", ephemeral=True)

    @commands.slash_command()
    @commands.has_permissions(manage_roles=True)
    async def banwords(self, inter: disnake.ApplicationCommandInteraction, words: str=commands.Param(description="Vesszővel(,) válazd el!")):
        await automod_definitions.InsertBannedWords(words)
        await inter.response.send_message(f"{words} sikeresen tiltva.", ephemeral=True)


    @commands.slash_command(description="List invite banned users.")
    @commands.has_permissions(manage_roles=True)
    async def listbans(self, inter: disnake.ApplicationCommandInteraction):
        embed = disnake.Embed(
            title="Invite bannolt userek:",
            description="",
            color=disnake.Color.red()
        )  
        bans = await automod_definitions.GetBanExpiries()
        for ban in bans:
            member = await self.bot.fetch_user(ban.userId)
            name = member.name
            embed.description += f'{member.name} {str(ban.BanExpiry.replace(tzinfo=None))[:-7]}\n'
        await inter.response.send_message(embed=embed)
    
    @commands.slash_command(description="List banned words")
    @commands.has_permissions(manage_roles=True)
    async def listwords(self, inter: disnake.ApplicationCommandInteraction):
        words = await automod_definitions.GetBannedWordList()
        embed = disnake.Embed(
            title=f'Bannolt szavak({len(words)}):',
            description="",
            color=disnake.Color.blurple()
        )
        if len(words) == 0:
            embed = disnake.Embed(
            title="Nincsenek még bannolt szavak!",
            description="",
            color=disnake.Color.red()
            )
            await inter.response.send_message(embed=embed)        
            return
        for word in words:
            embed.description += f'{word}\n'
        await inter.response.send_message(embed=embed)



def setup(bot):
    bot.add_cog(AutoMod(bot))