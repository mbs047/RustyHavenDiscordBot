from dotenv import load_dotenv
load_dotenv()

import discord, datetime, asyncio, os
from datetime import datetime


class Bot(discord.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.persistent_views_added = False
        
    async def on_ready(self):
        if not self.persistent_views_added:
            self.add_view(CreateTicket())
            self.add_view(TicketSetting())
            self.add_view(DeleteTicket())
            self.persistent_views_added = True
            print('Persistent views added')
        
        print(f'Bot is up and ready | Logged in as {self.user}')
    
    
class CreateTicket(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        
    @discord.ui.button(
        label = 'Create Ticket', 
        style = discord.ButtonStyle.primary, 
        custom_id = 'create_ticket:blurple',
        emoji = '🎫'
    )
    async def button_callback(self, button, interaction):
        try:
            category = discord.utils.get(interaction.guild.categories, name='OPENED_TICKETS')
            for ch in category.channels:
                if ch.topic == str(interaction.user.id):
                    return await interaction.response.send_message(f'{interaction.user.mention}! You already have a ticket {ch.mention}!', ephemeral=True, delete_after=10)
        except:
            await interaction.response.send_message('Hold up! working on your requiest', ephemeral=True, delete_after=10)
            
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages = False),
            interaction.user: discord.PermissionOverwrite(read_messages = True, view_channel = True),
            interaction.guild.get_role(os.environ.get('SUPPRT_ROLE_ID')): discord.PermissionOverwrite(read_messages = True, view_channel = True),
        }
        
        channel = await category.create_text_channel(name=f'{interaction.user.name}-{interaction.user.discriminator}', overwrites=overwrites, topic=f'{interaction.user.id}')
        embed = discord.Embed(
            title= 'New Ticket Created', 
            description= f'Ticket created by {interaction.user.mention}',
            timestamp= datetime.utcnow(),
            color= discord.Color.random()
        )
        await asyncio.sleep(2)
        await interaction.response.send_message(f'{channel.mention} click to go to ticket', ephemeral=True, delete_after=60)
        await channel.send(embed=embed, view = TicketSetting())


class TicketSetting(discord.ui.View):
    def __init__(self):
        super().__init__(timeout = None)
        
    @discord.ui.button(
        label = 'Close', 
        style = discord.ButtonStyle.gray,
        emoji = '🔒',
        custom_id = 'ticket_setting:gray'
    )
    async def close_ticket(self, button, interaction):
        if interaction.channel.category.id == os.environ.get('CLOSED_TICKET_CATEGORY_ID'):
            return await interaction.response.send_message("You can't use this command here", ephemeral=True, delete_after=60)
        
        await interaction.response.send_message('Closing Ticket', ephemeral=True, delete_after=60)
        
        category = discord.utils.get(interaction.guild.categories, name='CLOSED_TICKETS')
        channel = interaction.channel
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages = False),
            interaction.user: discord.PermissionOverwrite(read_messages = False, view_channel = False),
            interaction.guild.get_role(os.environ.get('SUPPRT_ROLE_ID')): discord.PermissionOverwrite(read_messages = True, view_channel = True),
        }
        await channel.edit(category=category, overwrites=overwrites)
        
        try:
            ticket = await interaction.guild.fetch_member(int(channel.topic))
            await channel.send(file=discord.File(f'{ticket.id}.txt'))
            os.remove(f'{ticket.id}.txt')
        except:
            print('Chat script not found')
            
        embed = discord.Embed(
            title= 'Delete Ticket', 
            description= f'Ticket will be deleted forever \nClosed at: {datetime.utcnow()}',
            color= discord.Color.random()
        )
        await channel.send(embed=embed, view = DeleteTicket())
        

class DeleteTicket(discord.ui.View):
    def __init__(self):
        super().__init__(timeout = None)
        
    @discord.ui.button(
        label = 'Delete', 
        style = discord.ButtonStyle.red,
        emoji = '🗑️',
        custom_id = 'ticket_setting:red'
    )
    async def close_ticket(self, button, interaction):
        if interaction.channel.category.id == os.environ.get('OPENED_TICKET_CATEGORY_ID'):
            return await interaction.response.send_message("The ticket must be closed first", ephemeral=True, delete_after=60)
    
        await interaction.response.send_message('Deleting Ticket')
        await asyncio.sleep(2)
        await interaction.channel.delete()
      

bot = Bot(activity=discord.Activity(type=discord.ActivityType.watching, name='B Bot'), intents=discord.Intents.all())


@bot.command(guild_ids=[os.environ.get('GUILD_IDS')], name='ping', description='Get Bot Latency')
async def ping(ctx):
    await ctx.respond(f'**Pong!** \nLatency: {round(bot.latency*1000)}ms', ephemeral=True, delete_after=5)
     

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    
    if message.channel.category.id == os.environ.get('OPENED_TICKET_CATEGORY_ID'):
        ticket = await message.guild.fetch_member(int(message.channel.topic))
        with open(f'{ticket.id}.txt', 'a') as file:
            file.write(f'Message from {message.author}: {message.content}\n')


@bot.command(guild_ids=[os.environ.get('GUILD_IDS')], description='Setup ticket widget')
async def setup_ticket(ctx):
    embed = discord.Embed(
        title = 'Create a ticket!',
        description = "Click the 'Create Ticket' button below to create a ticket. The server's staff will be notified and shortly aid with your problem."
    )
    await ctx.send(embed = embed, view = CreateTicket())


bot.run(os.environ.get('TOKEN'))