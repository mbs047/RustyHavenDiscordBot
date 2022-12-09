from datetime import datetime
from discord import Embed, ButtonStyle, AllowedMentions, utils, PermissionOverwrite
from discord.ui import View, button
from discord.ext.commands import Cog, command
import asyncio, random, humanfriendly
import time as PyTime
from blaster import Config


SETUP_TIMEOUT = 15
PING_WINNER_MESSAGE = True
USERS_REGISTERED = []

class JoinGiveAway(View):
    def __init__(self):
        super().__init__(timeout=None)
        
        
    @button(
        style = ButtonStyle.primary, 
        custom_id = 'JoinGiveAway:blurple',
        emoji = '🎉'
    )
    async def button_callback(self, button, interaction): 
        global USERS_REGISTERED
        
        role = utils.get(interaction.guild.roles, id=Config.SUPPRT_ROLE_ID)

        # if role in interaction.user.roles:
        #     return await interaction.response.send_message('Staff not allowed to enter', ephemeral=True, delete_after=10)
                
        if interaction.user not in USERS_REGISTERED:
            USERS_REGISTERED.append(interaction.user)
                        
            await interaction.response.send_message('You are registered now', ephemeral=True, delete_after=10)
        
        else:
            await interaction.response.send_message('You have registered before', ephemeral=True, delete_after=10)



class WinnerChannel(View):
    def __init__(self):
        super().__init__(timeout=None)
        
        
    @button(
        label='Giveway Given - Completed',
        style = ButtonStyle.success, 
        custom_id = 'WinnerChannel:blurple',
        emoji = '🎉'
    )
    async def button_callback(self, button, interaction):
        role = utils.get(interaction.guild.roles, id=Config.SUPPRT_ROLE_ID)

        if role in interaction.user.roles:
            embed = Embed(
                title= 'Winner channel will be deleted in a few seconds', 
                color= 0xFF0000
            )
            await interaction.response.send_message(embed=embed)
            await asyncio.sleep(2)
            await interaction.channel.delete()

        else:
            embed = Embed(
                title= 'You are not allowed to do that', 
                color= 0xFF0000
            )
            await interaction.response.send_message(embed=embed)


class Giveaway(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.persistent_views_added = False


    @Cog.listener()
    async def on_ready(self):
        if not self.persistent_views_added:
            self.bot.add_view(JoinGiveAway())
            self.bot.add_view(WinnerChannel())
            self.persistent_views_added = True
            print(' ---> Giveaway persistent views added')
           
            
    @command(name='giveaway')
    async def giveaway(self, ctx):
        global USERS_REGISTERED
        
        question_one = Embed(
            title=":gift: | SETUP WIZARD",
            description=f"Welcome to the Setup Wizard. Answer the following questions within ``{SETUP_TIMEOUT}`` Seconds!"
        ).add_field(
            name=":star: | Question 1",
            value="Where should we host the Giveaway?\n\n **Example**: ``#General``"
        )
        
        question_two = Embed(
            title=":gift: | SETUP WIZARD",
            description="Great! Let's move onto the next question."
        ).add_field(
            name=":star: | Question 2",
            value="How long should it last? ``<s|m|h|d|w>``\n\n **Example**: ``1d``"
        )
        
        question_three = Embed(
            title=":gift: | SETUP WIZARD",
            description="Great! Let's move onto the next question."
        ).add_field(
            name=":star: | Question 3",
            value="How many winners can receive the prize?\n\n **Example**: ``5``"
        )
        
        question_four = Embed(
            title=":gift: | SETUP WIZARD",
            description="Awesome. You've made it to the last question!"
        ).add_field(
            name=":star: | Question 2",
            value="What is the prize the winner will receive?\n\n **Example**: ``NITRO``"
        )

        questions = [question_one, question_two, question_three, question_four]
        answers = []

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        for index, question in enumerate(questions):
            if index == 0:
                questionOut = await ctx.send(embed=question)
            
            else:
                await questionOut.edit(embed=question)

            try:
                msg = await self.bot.wait_for('message', timeout=SETUP_TIMEOUT, check=check)
                
            except asyncio.TimeoutError:
                timedOut = Embed(
                    title=":gift: **Giveaway Setup Wizard**",
                    description=":x: You didn't answer in time!"
                )
                
                await ctx.send(embed=timedOut, delete_after=SETUP_TIMEOUT)
                return
            
            else:
                answers.append(msg.content)
                await msg.delete()

        questionOut.delete()

        try:
            c_id = int(answers[0][2: -1])
            
        except:
            incorrectChannel = Embed(
                title=":gift: **Giveaway Setup Wizard**",
                description=":x: You didn't specify a channel correctly!"
            )
            
            await ctx.send(embed=incorrectChannel, delete_after=SETUP_TIMEOUT)
            return

        channel = self.bot.get_channel(c_id)

        if convert(answers[1]) <= -1:
            incorrectUnit = Embed(
                title=":gift: **Giveaway Setup Wizard**",
                description=":x: You didn't set a proper time unit!"
            )
        
            await ctx.send(embed=incorrectUnit, delete_after=SETUP_TIMEOUT)
            return
    
        setupConfirmationEmbed = Embed(
            title=":gift: **Giveaway Setup Wizard**", 
            description="Okay, all set. The Giveaway will now begin!"
        ).add_field(
            name="Hosted Channel:",
            value=f"{channel.mention}"
        ).add_field(
            name="Time:", 
            value=f"<t:{int(PyTime.time() + humanfriendly.parse_timespan(answers[1]))}:R>"
        ).add_field(
            name="Prize:",
            value=answers[3]
        )
        
        await ctx.send(embed=setupConfirmationEmbed, delete_after=SETUP_TIMEOUT)
    
        embed = Embed(
            title=f":gift: **GIVEAWAY FOR: {answers[3]}**",
            description="React With 🎉 To Participate!",
            timestamp=datetime.utcnow()
        ).add_field(
            name="Ends:", 
            value=f"<t:{int(PyTime.time() + humanfriendly.parse_timespan(answers[1]))}:R> (<t:{int(PyTime.time() + humanfriendly.parse_timespan(answers[1]))}:f>)",
            inline=False
        ).add_field(
            name=f"Hosted By:", 
            value=ctx.author.mention,
            inline=False
        ).add_field(
            name=f"Possible Winners:", 
            value=answers[2],
            inline=False
        )
        
        await channel.send("@everyone Giveaway Live.", allowed_mentions=AllowedMentions(everyone = True), delete_after=60*60*24)
        await channel.send(embed=embed, view=JoinGiveAway(), delete_after=60*60*24)
        await asyncio.sleep(convert(answers[1]))
        
        for winnerDraw in range (int(answers[2])):
            if len(USERS_REGISTERED) > 0:
                winner = random.choice(USERS_REGISTERED)
                if PING_WINNER_MESSAGE == True:
                    await channel.send(f":tada: Congratulations! {winner.mention} won: **{answers[3]}**!", delete_after=60*60)

                winnerEmbed = Embed(
                    title=f":gift: **GIVEAWAY FOR: {answers[3]}**",
                    description=f":trophy: **Winner:** {winner.mention}"
                ).set_footer(
                    text="Giveaway Has Ended"
                )
                
                category = utils.get(ctx.guild.categories, id=Config.MAIN_SERVER_CATEGORY_ID)     
                overwrites = {
                    ctx.guild.default_role: PermissionOverwrite(read_messages=False),
                    winner: PermissionOverwrite(read_messages=True),
                    ctx.guild.get_role(Config.SUPPRT_ROLE_ID): PermissionOverwrite(read_messages = True, view_channel = True),
                } 
                winnerChannel = await category.create_text_channel(name=f'Giveaway claim - {winner.name}', topic=f'{winner.id}', overwrites=overwrites)
                embed = Embed(
                    title='Congratulations',
                    description= f'{ctx.author.mention} you win the giveaway. <@&{Config.SUPPRT_ROLE_ID}> will be with you soon, to give you the prize',
                    timestamp= datetime.utcnow(),
                    color= 0x2ECC71
                )
                
                await channel.send(embed=winnerEmbed, delete_after=60*60)
                await winnerChannel.send(embed=embed, view = WinnerChannel())
                USERS_REGISTERED.remove(winner)
                
        USERS_REGISTERED = []

            
            
def convert(time):
    pos = ["s", "m", "h", "d", "w"]
    time_dict = {"s": 1, "m": 60, "h": 3600, "d": 3600 * 24, "w": 3600 * 24 * 7}
    unit = time[-1]

    if unit not in pos:
        return -1
    try:
        val = int(time[:-1])
    except:
        return -2

    return val * time_dict[unit]



def setup(bot):
    bot.add_cog(Giveaway(bot))