import sys
import asyncio
from discord.ext.commands import Bot

# CONFIG
TOKEN = sys.argv[1]
headers = {}
headers['Api-Key'] = sys.argv[2]

client = Bot(command_prefix='')

@client.event  # 0004
async def on_ready():
        print("-> " + client.user.name + " Instance is ONLINE")
        server = client.get_guild(162706186272112640)
        temp = 0
        for member in server.members:
                print(str(member.display_name))
                temp = temp + 1
        print('TOTAL MEMBERS: %d', temp)
        print("-> " + client.user.name + " Instance is OFFLINE")
        sys.exit(0)


client.run(TOKEN, bot=True, reconnect=True)