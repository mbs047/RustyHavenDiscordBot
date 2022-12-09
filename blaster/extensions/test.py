from asyncio import sleep
from typing import Optional
from datetime import timedelta, datetime
from discord import Member, Embed, utils
from discord.ext.commands import Cog, command, bot_has_permissions, has_permissions, Greedy, CheckFailure
from blaster.database import database
from blaster import Config


class Test(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_channel = self.bot.get_channel(Config.BOT_LOG_CHANNEL_ID)

        
    async def mute_members(self, message, targets, hours, reason, mute_role):
        unmutes = []

        for target in targets:
            if not mute_role in target.roles:
                if message.guild.me.top_role.position > target.top_role.position:
                    role_ids = ",".join([str(r.id) for r in target.roles])
                    end_time = datetime.utcnow() + timedelta(seconds=hours) if hours else None

                    database.execute("INSERT OR REPLACE INTO mutes VALUES (?, ?, ?)",
                                target.id, role_ids, getattr(end_time, "isoformat", lambda: None)())

                    await target.edit(roles=[mute_role])

                    embed = Embed(title="Member muted",
                                    colour=0xDD2222,
                                    timestamp=datetime.utcnow())

                    embed.set_thumbnail(url=target.display_avatar.url)
                    embed.set_footer(text=f'{message.author.name}#{message.author.discriminator}', icon_url=message.author.display_avatar.url)
                    
                    fields = [("Member", target.mention, True),
                                ("Duration", f"{hours:,} hour(s)" if hours else "Indefinite", True),
                                ("Reason", reason, False)]

                    for name, value, inline in fields:
                        embed.add_field(name=name, value=value, inline=inline)

                    await self.bot.get_channel(Config.BOT_LOG_CHANNEL_ID).send(embed=embed)

                    if hours:
                        unmutes.append(target)

        return unmutes

    @command(name="mute")
    @bot_has_permissions(manage_roles=True)
    @has_permissions(manage_roles=True, manage_guild=True)
    async def mute_command(self, ctx, targets: Greedy[Member], hours: Optional[int], *, reason: Optional[str] = "No reason provided."):
        if not len(targets):
            await ctx.send("One or more required arguments are missing.")

        else:
            mute_role = ctx.guild.get_role(1049081863404261427)
            unmutes = await self.mute_members(ctx.message, targets, hours, reason, mute_role)
            await ctx.send("Action complete.")

            if len(unmutes):
                await sleep(hours)
                await self.unmute_members(ctx.guild, targets, mute_role)

    @mute_command.error
    async def mute_command_error(self, ctx, exc):
        if isinstance(exc, CheckFailure):
            await ctx.send("Insufficient permissions to perform that task.")

    async def unmute_members(self, guild, targets, mute_role, reason="Mute time expired."):
        for target in targets:
            if mute_role in target.roles:
                role_ids = database.field("SELECT RoleIDs FROM mutes WHERE UserID = ?", target.id)
                roles = [guild.get_role(int(id_)) for id_ in role_ids.split(",") if len(id_)]

                database.execute("DELETE FROM mutes WHERE UserID = ?", target.id)

                await target.edit(roles=roles)

                embed = Embed(title="Member unmuted",
                                colour=0xDD2222,
                                timestamp=datetime.utcnow())

                embed.set_thumbnail(url=target.display_avatar.url)

                fields = [("Member", target.mention, False),
                            ("Reason", reason, False)]

                for name, value, inline in fields:
                    embed.add_field(name=name, value=value, inline=inline)

                await self.log_channel.send(embed=embed)
        


def setup(bot):
    bot.add_cog(Test(bot))