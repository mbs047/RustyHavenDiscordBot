import time
from datetime import datetime
from discord import Member, Embed
from discord.ext.commands import Cog, command, has_permissions, cooldown, BucketType
from typing import Optional


class Info(Cog):
    def __init__(self, bot):
        self.bot = bot


    # Ping Command
    @command(name='ping', aliases=['Latency'], description='Get Bot Latency')
    @cooldown(1, 60, BucketType.user)
    @has_permissions(administrator=True)
    async def ping(self, ctx):
        msg = await ctx.send("`Bot Latency...`")
        times = []
        counter = 0
        embed = Embed(
            title= "More Information:", 
            description= "4 pings have been made and here are the results:", 
            colour= 0xFF0000
        )
        for _ in range(3):
            counter += 1
            start = time.perf_counter()
            await msg.edit(content=f"Trying Ping... {counter}/3")
            
            end = time.perf_counter()
            speed = round((end - start) * 1000)
            times.append(speed)
            
            if speed < 160:
                embed.add_field(name=f"Ping {counter}:", value=f"🟢 | {speed}ms", inline=True)
                
            elif speed > 170:
                embed.add_field(name=f"Ping {counter}:", value=f"🟡 | {speed}ms", inline=True)
                
            else:
                embed.add_field(name=f"Ping {counter}:", value=f"🔴 | {speed}ms", inline=True)
                
        embed.set_author(name="🏓    **PONG**    🏓", icon_url="https://img.icons8.com/ultraviolet/40/000000/table-tennis.png")
        embed.add_field(name="Bot Latency", value=f"{round(self.bot.latency * 1000)}ms", inline=True)
        embed.add_field(name="Normal Speed", value=f"{round((round(sum(times)) + round(self.bot.latency * 1000))/4)}ms")
        embed.set_footer(text=f"Total estimated elapsed time: {round(sum(times))}ms")
        
        await msg.edit(content=f":ping_pong: **{round((round(sum(times)) + round(self.bot.latency * 1000))/4)}ms**", embed=embed)

   
    # User details 
    @command(name="userinfo", aliases=["memberinfo", "ui", "mi"])
    @has_permissions(administrator=True)
    async def user_info(self, ctx, target: Optional[Member]):
        target = target or ctx.author

        embed = Embed(
            title="User information",
            colour=target.colour,
            timestamp=datetime.utcnow()
        )
        
        embed.set_thumbnail(url=target.avatar)
        
        fields = [("Name", str(target), True),
                    ("ID", target.id, True),
                    ("Bot?", target.bot, True),
                    ("Top role", target.top_role.mention, True),
                    ("Status", str(target.status).title(), True),
                    ("Activity", f"{str(target.activity.type).split('.')[-1].title() if target.activity else 'N/A'} {target.activity.name if target.activity else ''}", True),
                    ("Created at", target.created_at.strftime("%d/%m/%Y %H:%M:%S"), True),
                    ("Joined at", target.joined_at.strftime("%d/%m/%Y %H:%M:%S"), True),
                    ("Boosted", bool(target.premium_since), True)]

        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)

        await ctx.send(embed=embed)
        
        
    # Server details
    @command(name="serverinfo", aliases=["guildinfo", "si", "gi"])
    @has_permissions(administrator=True)
    async def server_info(self, ctx):
        embed = Embed(title="Server information",
                        colour=ctx.guild.owner.colour,
                        timestamp=datetime.utcnow())

        embed.set_thumbnail(url=ctx.guild.icon)

        statuses = [len(list(filter(lambda m: str(m.status) == "online", ctx.guild.members))),
                    len(list(filter(lambda m: str(m.status) == "idle", ctx.guild.members))),
                    len(list(filter(lambda m: str(m.status) == "dnd", ctx.guild.members))),
                    len(list(filter(lambda m: str(m.status) == "offline", ctx.guild.members)))]

        fields = [("ID", ctx.guild.id, True),
                    ("Owner", ctx.guild.owner, True),
                    ("Created at", ctx.guild.created_at.strftime("%d/%m/%Y %H:%M:%S"), True),
                    ("Members", len(ctx.guild.members), True),
                    ("Humans", len(list(filter(lambda m: not m.bot, ctx.guild.members))), True),
                    ("Bots", len(list(filter(lambda m: m.bot, ctx.guild.members))), True),
                    ("Statuses", f"🟢 {statuses[0]} 🟠 {statuses[1]} 🔴 {statuses[2]} ⚪ {statuses[3]}", True),
                    ("Text channels", len(ctx.guild.text_channels), True),
                    ("Voice channels", len(ctx.guild.voice_channels), True),
                    ("Categories", len(ctx.guild.categories), True),
                    ("Roles", len(ctx.guild.roles), True),
                    ("Invites", len(await ctx.guild.invites()), True),
                    ("\u200b", "\u200b", True)]

        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)

        await ctx.send(embed=embed)
        

def setup(bot):
    bot.add_cog(Info(bot))