import requests
import discord
from discord import app_commands
from discord.ext import commands

TOKEN = 'MTA0MzQwODk3OTQ3NDI1OTk4OA.GudDnK.I0IIJ2pnvuG_l5wdP4zWdqyy0NjOJGRHr96xXM'
api_url = "https://dummyjson.com/posts?skip=5&limit=5"

# client = discord.Client(intents=discord.Intents.all())
bot = commands.Bot(command_prefix="/", intents=discord.Intents.all())


@bot.event
async def on_ready():
    print('We have logged in as {0.user}' . format(bot))
    print(f'Synced {len(await bot.tree.sync())} command(s)')


@bot.tree.command(name='hello')
async def hello(interaction: discord.Integration):
    await interaction.response.send_message(f'Hello {interaction.user.mention}!',  ephemeral=True)


@bot.tree.command(name='api')
async def api(interaction: discord.Integration):
    response = requests.get(api_url+'1').json()
    await interaction.response.send_message(f'{response["title"]}',  ephemeral=True)


@bot.tree.command(name='report')
@app_commands.describe(steamid='Enter the cheater steam id', message="Write a message")
async def report(interaction: discord.Integration, steamid: str, message: str):
    await bot.get_channel(1043418778622504981).send(f'{interaction.user.mention}, reported: {steamid}, \n message: {message}')
    await interaction.response.send_message(f'Thank you for reporting {steamid}, we have someone checking on him now.',  ephemeral=True)
    
    
@bot.tree.command(name='wipe')
async def wipe(interaction: discord.Integration):
    await interaction.response.send_message.send("text",  ephemeral=True)


@bot.event
async def on_message(message):
    username = str(message.author).split('#')[0]
    user_mention = f'<@{message.author.id}>'
    user_message = str(message.content).lower()
    channel = str(message.channel.name) if message.guild else'Private'
    print(f'{username}: {user_message} ({channel})')
    if message.author == bot.user:
        return

    # Specific a channel for commands
    # if message.channel.name == 'general':
    
    reportHackerKeywords = ['hacker', 'hack', 'cheater', 'cheating']
    if any(word in user_message for word in reportHackerKeywords):
        await message.delete()
        await message.author.send(f'Hi {user_mention}, please use !report to report!')
        return
    elif user_message == 'apple':
        await message.add_reaction('\U0001F34E')
    elif user_message == 'car':
        await message.add_reaction('\U0001F697')
    elif user_message == 'cool':
        await message.add_reaction('\U0001F192')
    

@bot.event
async def on_message_edit(before, after):
    if before.author == bot.user:
        return
    
    await bot.get_channel(1043797619576672337).send(
        f'{before.author.mention} edited a message. \n'
        f'Channel: {before.channel.name}. \n'
        f'Before: {before.content} \n'
        f'After: {after.content}'
    )
    
    
@bot.event
async def on_message_delete(message):
    if message.author == bot.user:
        return
    
    await bot.get_channel(1043797619576672337).send(
        f'{message.author.mention} deleted a message. \n'
        f'Channel: {message.channel.name}. \n'
        f'Message: {message.content}'
    )


bot.run(TOKEN)
