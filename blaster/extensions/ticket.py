import asyncio, os
from discord import utils, PermissionOverwrite, File, Embed, ButtonStyle, Interaction
from discord.ui import View, button
from discord.ext.commands import command, Cog, has_permissions
from datetime import datetime
from blaster import Config


class Ticket(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.persistent_views_added = False


    @Cog.listener()
    async def on_ready(self):
        if not self.persistent_views_added:
            self.bot.add_view(CreateTicket())
            self.bot.add_view(TicketSetting())
            self.bot.add_view(DeleteTicket())
            self.persistent_views_added = True
            print(' ---> Ticket persistent views added')
    
    
    @command(description='Setup ticket widget')
    @has_permissions(administrator=True)
    async def setup_ticket(self, ctx):
        embed = Embed(
            title = f'{ctx.guild.name} Support',
            description = f"Welcome to {ctx.guild.name} Support!\n\nIf you are reporting a player, please specify the server name, the player's name and any relevant screenshots or video evidence. Please have your steamid ready for any support specific to you,"
        )
        await ctx.send(embed=embed, view=CreateTicket())
        
        
    @command(description='Delete Ticket Channel')
    @has_permissions(ban_members=True)
    async def delete_ticket(self, interaction):
        await interaction.channel.delete()
    
        
    @Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        
        # Helpers
        channel = message.channel
        
        # To save tickets trascripts
        try:
            if channel.category.id == Config.OPENED_TICKET_CATEGORY_ID:
                ticket = await message.guild.fetch_member(int(channel.topic))
                with open(f'{ticket.id}.txt', 'a') as file:
                    file.write(f'Message from {message.author}: {message.content}\n')
        except:
            print('No Ticket Channels Found')
            
            
    
class CreateTicket(View):
    def __init__(self):
        super().__init__(timeout=None)
        
        
    @button(
        label = 'Create Ticket', 
        style = ButtonStyle.primary, 
        custom_id = 'create_ticket:blurple',
        emoji = '🎫'
    )
    async def button_callback(self, button, interaction):
        category = utils.get(interaction.guild.categories, id=Config.OPENED_TICKET_CATEGORY_ID)       
        try:
            for ch in category.channels:
                if ch.topic == str(interaction.user.id):
                    return await interaction.response.send_message(f'{interaction.user.mention}! You already have a ticket {ch.mention}!', ephemeral=True, delete_after=10)
        except:
            await interaction.response.send_message('Hold up! working on your requiest', ephemeral=True, delete_after=10)
            
        overwrites = {
            interaction.guild.default_role: PermissionOverwrite(read_messages = False),
            interaction.user: PermissionOverwrite(read_messages = True, view_channel = True),
            interaction.guild.get_role(Config.SUPPRT_ROLE_ID): PermissionOverwrite(read_messages = True, view_channel = True),
        }
        
        channel = await category.create_text_channel(name=f'{interaction.user.name}-{interaction.user.discriminator}', overwrites=overwrites, topic=f'{interaction.user.id}')
        embed = Embed(
            description= f'{interaction.user.mention} Welcome to support. <@&{Config.SUPPRT_ROLE_ID}> will be with you soon. If this has to do with a donation or specific issue to you please have your steamid ready.\nTo close this ticket react with 🔒',
            timestamp= datetime.utcnow(),
            color= 0x2ECC71
        )
        await asyncio.sleep(2)
        await interaction.response.send_message(f'{channel.mention} click to go to ticket', ephemeral=True, delete_after=60)
        await channel.send(embed=embed, view = TicketSetting())



class TicketSetting(View):
    def __init__(self):
        super().__init__(timeout = None)
       
        
    @button(
        label = 'Close', 
        style = ButtonStyle.gray,
        emoji = '🔒',
        custom_id = 'ticket_setting:gray'
    )
    async def close_ticket(self, button, interaction):        
        if interaction.channel.category.id == Config.CLOSED_TICKET_CATEGORY_ID:
            return await interaction.response.send_message("You can't use this command here", ephemeral=True, delete_after=60)
        
        await interaction.response.send_message('Are you sure you would like to close this ticket?', view = ConfirmClosingTicket(), ephemeral=True, delete_after=10)
    
    
          
class ConfirmClosingTicket(View):
    def __init__(self):
        super().__init__(timeout = None)
      
        
    @button(
        label = 'Close', 
        style = ButtonStyle.red,
        custom_id = 'ticket_setting:red'
    )
    async def close(self, button, interaction):
        if interaction.channel.category.id == Config.CLOSED_TICKET_CATEGORY_ID:
            return await interaction.response.send_message("You can't use this command here", ephemeral=True, delete_after=60)
        
        embed = Embed(
            title= f'Ticket Closed by {interaction.user.mention}',
            color= 0xF1C40F
        )
        await interaction.response.send_message(embed=embed)
        
        category = utils.get(interaction.guild.categories, id=Config.CLOSED_TICKET_CATEGORY_ID)
        channel = interaction.channel
        overwrites = {
            interaction.guild.default_role: PermissionOverwrite(read_messages = False),
            interaction.user: PermissionOverwrite(read_messages = False, view_channel = False),
            interaction.guild.get_role(Config.SUPPRT_ROLE_ID): PermissionOverwrite(read_messages = True, view_channel = True),
        }
        await channel.edit(category=category, overwrites=overwrites)
        
        try:
            ticket = await interaction.guild.fetch_member(int(channel.topic))
            await channel.send(file=File(f'{ticket.id}.txt'))
            os.remove(f'{ticket.id}.txt')
        except:
            print('Chat script not found')
            
        embed = Embed(
            title= 'Delete Ticket', 
            description= f'Ticket will be deleted forever \nClosed at: {datetime.utcnow()}',
            color= 0xFF0000
        )
        await channel.send(embed=embed, view = DeleteTicket())
    
        

class DeleteTicket(View):
    def __init__(self):
        super().__init__(timeout = None)
     
        
    @button(
        label = 'Delete', 
        style = ButtonStyle.red,
        emoji = '🗑️',
        custom_id = 'ticket_setting:red'
    )
    async def delete(self, button, interaction):
        if interaction.channel.category.id == Config.OPENED_TICKET_CATEGORY_ID:
            return await interaction.response.send_message("The ticket must be closed first", ephemeral=True, delete_after=60)
    
        embed = Embed(
            title= 'Ticket will be deleted in a few seconds', 
            color= 0xFF0000
        )
        await interaction.response.send_message(embed=embed)
        await asyncio.sleep(2)
        await interaction.channel.delete()
          
    
    
def setup(bot):
    bot.add_cog(Ticket(bot))