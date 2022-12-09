from os.path import exists
from glob import glob
from aiohttp import request
from discord import Intents, Activity, ActivityType
from discord.errors import Forbidden
from discord.ext.commands import Bot as BotBase
from discord.ext.commands import has_permissions
from discord.ext.commands import (CommandNotFound, BadArgument, MissingRequiredArgument, CommandOnCooldown, MissingPermissions)
from blaster import Config
from asyncio import sleep

COGS_PATH = 'blaster.extensions.'
EXTENSIONS_PATH = './blaster/extensions/'
COGS = [path.split("\\")[-1][:-3] for path in glob(f"{EXTENSIONS_PATH}*.py")]

bot = BotBase(command_prefix=Config.PREFIX, intents=Intents.all())


class LoadCogs():
    def send_data(data):
        return data
    
    data = []
    if Config.LOAD_COGS_ON_START == 'True':
        print('Running Cogs...')
        
        for cog in COGS:
            try:
                bot.load_extension(f'{COGS_PATH}{cog}')
                print(f' - "{cog}" Cog Loaded Successfully')
                data.append(f' - "{cog}" Cog Loaded Successfully')

            except Exception as e:
                print(f' - "{cog}" Cog Not loaded: {e}')
                data.append(f' - "{cog}" Cog Not loaded: {e}')
            
        print(f'Cogs Loaded Successfully')
        
    send_data(data)
        
    



async def status_update():
    await bot.wait_until_ready()
    while True:
        try:
            fact_url = f'https://rust-servers.net/api/?object=servers&element=detail&key={Config.RUST_SERVERS_NET_API}'

            async with request("GET", fact_url, headers={}) as response:
                if response.status == 200:
                    data = await response.json(content_type='text/html')
                    message = f"{data['is_online']} / {data['maxplayers']} Online"

                else:
                    message = 'Server Offline'
        except:
            message = 'Server Offline'

        await bot.change_presence(activity=Activity(type=ActivityType.watching, name=message))
        await sleep(60)
        # print(f" - Status Updated -> {message}")
        

@bot.event
async def on_ready():
    await LoadCogs()
    print('Bot is up and ready!')


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, BadArgument):
        pass

    elif isinstance(error, MissingRequiredArgument):
        await ctx.send('***Warning***: [001] One or more required arguments are missing.')

    elif isinstance(error, MissingPermissions):
        await ctx.send('***Warning***: [002] Insufficient permissions to perform that task')
        
    elif isinstance(error, CommandNotFound):
        await ctx.send('***Warning***: [003] Command not found!')

    elif isinstance(error, CommandOnCooldown):
        await ctx.send(f"***Warning***: [004] You're doing that too quickly, try again in {error.retry_after:,.2f}s.")

    elif hasattr(error, 'original'):
        if isinstance(error.original, Forbidden):
            await ctx.send('***Warning***: [005] I do not have permission to do that.')

        else:
            raise error.original

    else:
        raise error
 
 
@bot.command(name='load')
@has_permissions(administrator=True)
async def load(ctx, extension):
    if ctx.channel.id != Config.BOT_COMMAND_CHANNEL_ID:
        return

    if extension == 'all':
        data = await LoadCogs()
        for cog in data:
            await ctx.send(cog)
        return

    if exists(f'{EXTENSIONS_PATH}{extension}.py'):
        try:
            bot.load_extension(f'{COGS_PATH}{extension}')
            await ctx.send(f'Loaded {extension} Successfully!')
        except:
            await ctx.send(f'{extension} is already loaded!')
        
    else:
        await ctx.send(f'Cog not found!')
    

@bot.command(name='unload')
@has_permissions(administrator=True)
async def unload(ctx, extension):
    if ctx.channel.id != Config.BOT_COMMAND_CHANNEL_ID:
        return
    
    if exists(f'{EXTENSIONS_PATH}{extension}.py'):
        try:
            bot.unload_extension(f'{COGS_PATH}{extension}')
            await ctx.send(f'Unloaded {extension} Successfully!')
        except:
            await ctx.send(f'{extension} is already unloaded!')
        
    else:
        await ctx.send(f'Cog not found!')
    
    
@bot.command(name='reload')
@has_permissions(administrator=True)
async def reload(ctx, extension):
    if ctx.channel.id != Config.BOT_COMMAND_CHANNEL_ID:
        return
    
    if exists(f'{EXTENSIONS_PATH}{extension}.py'):
        bot.reload_extension(f'{COGS_PATH}{extension}')
        await ctx.send(f'Reloaded {extension} Successfully!')
        
    else:
        await ctx.send(f'Cog not found!')


bot.loop.create_task(status_update()) 
bot.run(Config.TOKEN)
