from aiohttp import request
from discord import Embed
from discord.ext.commands import Cog, command, cooldown, BucketType
from blaster import Config


class Players(Cog):
    def __init__(self, bot):
        self.bot = bot
        
        
    @command(name="players")
    @cooldown(1, 60, BucketType.user)
    async def players(self, ctx):
        await ctx.message.delete()
        
        fact_url = f'https://rust-servers.net/api/?object=servers&element=detail&key={Config.RUST_SERVERS_NET_API}'

        async with request("GET", fact_url, headers={}) as response:
            if response.status == 200:
                data = await response.json(content_type='text/html')

                embed = Embed(
                    title=f"{data['is_online']} / {data['maxplayers']} Online",
                    description=data['hostname'],
                    colour=ctx.author.colour
                )

                await ctx.send(embed=embed)
            else:
                await ctx.send(f"API returned a {response.status} status.")
            
            

def setup(bot):
    bot.add_cog(Players(bot))