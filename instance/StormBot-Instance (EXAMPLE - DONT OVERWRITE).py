import sys
import asyncio
from discord.ext.commands import Bot
'''To Use this Instance oy u must use this code in the main StormBot file
 import os;
        my_dir = os.path.dirname(sys.argv[0])
        os.system('%s %s %s %s' % (sys.executable,
                                os.path.join(my_dir, 'StormBot-Instance.py'),
                                TOKEN, APIKEY))
'''

# CONFIG
TOKEN = sys.argv[1]
headers = {}
headers['Api-Key'] = sys.argv[2]

client = Bot()


@client.event  # 0004
async def on_ready():
        print("-> " + client.user.name + " Instance is ONLINE")
        await asyncio.sleep(20)
        print("-> " + client.user.name + " Instance is OFFLINE")
        sys.exit(0)


client.run(TOKEN, bot=True, reconnect=True)