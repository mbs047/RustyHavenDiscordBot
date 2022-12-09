from discord import Forbidden, Embed
from discord.ext.commands import Cog
from datetime import datetime
from blaster import Config


class Welcome(Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @Cog.listener()
    async def on_member_join(self, member):
        await self.bot.get_channel(Config.WELCOME_CHANNEL_ID).send(embed=Embed(
            title=f'Welcome',
            description=f'{member.mention} Joined {member.guild.name}',
            color=0xFF0000,
            timestamp=datetime.utcnow()
        ).add_field(
            name=f':hey: Rules',
            value=f'<#{Config.RULES_CHANNEL_UD}>'
        ).add_field(
            name=f':hey: Chat',
            value=f'<#{Config.GENERAL_CHANNEL_ID}>'
        ).add_field(
            name=f'Total members',
            value=f'{member.guild.member_count}'
        ).set_footer(
            text=f'{member.name} just joined'
        ))

        try:
            await member.send(f"Welcome to **{member.guild.name}**! Enjoy your stay!")

        except Forbidden:
            pass

        await member.add_roles(member.guild.get_role(Config.USER_DEFAULT_ROLE_ID))  # Can add more roles using comma


    @Cog.listener()
    async def on_member_remove(self, member):
        return
        await self.bot.get_channel(Config.WELCOME_CHANNEL_ID).send(f"{member.display_name} has left {member.guild.name}.")
        
        

def setup(bot):
    bot.add_cog(Welcome(bot))