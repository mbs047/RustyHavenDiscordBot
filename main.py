import discord
from decouple import config
import random

TOKEN = 'MTA0MzQwODk3OTQ3NDI1OTk4OA.GudDnK.I0IIJ2pnvuG_l5wdP4zWdqyy0NjOJGRHr96xXM'

client = discord.Client(intents=discord.Intents.all())


@client.event
async def on_ready():
    print('We have logged in as {0.user}' . format(client))


@client.event
async def on_message(message):
    username = str(message.author).split('#')[0]
    user_mention = f'<@{message.author.id}>'
    user_message = str(message.content).lower()
    if message.guild:
        channel = str(message.channel.name)
    else:
        channel = 'Private'
    print(f'{username}: {user_message} ({channel})')

    if message.author == client.user:
        return

    # Specific a channel for commands
    if message.channel.name == 'general':
        reportHackerKeywords = ['hacker', 'hack', 'cheater', 'cheating']

        if any(word in user_message for word in reportHackerKeywords):
            await message.delete()
            await message.author.send(f'Hi {user_mention}, please use !report to report!')
            return

        elif user_message.lower() == 'reply':
            await message.reply(f'Hi {user_mention}, please use !report to report!')
            return

        elif user_message.lower() == '!report':

            # Global commands
    if user_message.lower() == '!anywhere':
        await message.channel.send(f'Anywhere!')
        return

client.run(config('TOKEN'))
