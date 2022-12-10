from asyncio import sleep
from typing import Optional
from datetime import timedelta, datetime
from discord import Member, Embed, utils
from discord.ext.commands import Cog, command, bot_has_permissions, has_permissions, Greedy, CheckFailure
from blaster.database import database


class Test(Cog):
    def __init__(self, bot):
        self.bot = bot


    @command(name='test')
    async def test(self, ctx):
        res = database.execute(prefix='test', data={'name': 'Hi World'})
        
        await ctx.send(res)
        
    

def setup(bot):
    bot.add_cog(Test(bot))