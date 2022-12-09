from datetime import datetime, timedelta
from discord import Member, Embed, Interaction
from discord.ext.commands import Cog, command, Greedy, has_permissions, bot_has_permissions
from typing import Optional
from blaster import Config


class Mod(Cog):
    def __init__(self, bot):
        self.bot = bot

        
    @command(name="clear", aliases=["purge"])
    @bot_has_permissions(manage_messages=True)
    @has_permissions(administrator=True)
    async def clear_messages(self, interaction: Interaction, targets: Greedy[Member], limit: Optional[int] = 1):
        def _check(message):
            return not len(targets) or message.author in targets

        if 0 < limit <= 500:
            with interaction.channel.typing():
                await interaction.message.delete()
                deleted = await interaction.channel.purge(limit=limit, after=datetime.utcnow() - timedelta(days=14), check=_check)

                if len(targets) > 0:
                    target = targets[0].mention
                else:
                    target = 'All Users'

                embed = Embed(
                    title='Messages Purged',
                    timestamp=datetime.utcnow(),
                    color=0x2ECC71
                )
                embed.add_field(name='Channel', value=interaction.channel.mention, inline=True)
                embed.add_field(name='Target', value=target, inline=True)
                embed.add_field(name='Number Of Messages', value=f"Deleted {len(deleted):,} messages.", inline=True)
                embed.set_author(
                    name=f'{interaction.author.name}#{interaction.author.discriminator}',
                    icon_url=f'{interaction.author.avatar}'
                )
                await self.bot.get_channel(Config.BOT_LOG_CHANNEL_ID).send(embed=embed, reference=interaction.message.reference)

        else:
            await interaction.response.send_message("The limit provided is not within acceptable bounds.")


def setup(bot):
    bot.add_cog(Mod(bot))