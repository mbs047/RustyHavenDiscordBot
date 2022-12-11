from aiohttp import request
from discord import Intents, Activity, ActivityType
from discord.ext.commands import Bot as BotBase
from ServerStatus.blaster import Config
from asyncio import sleep

bot = BotBase(command_prefix=Config.PREFIX, intents=Intents.all())


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
        
        print(f" - Status Updated -> {message}")
        

@bot.event
async def on_ready():
    print('Bot is up and ready!')


bot.loop.create_task(status_update()) 
bot.run(Config.TOKEN)
