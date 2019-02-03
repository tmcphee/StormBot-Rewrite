import discord
import asyncio
import datetime
import requests

text_file = open("StormBot.config", "r")
BOT_CONFIG = text_file.readlines()
text_file.close()
api_url = str(BOT_CONFIG[1]).strip()


async def msg_broadcast(client):
    # Will post random broadcast in each of the channel ID's in this list
    broadcast_list = [384886471531692033, 162706186272112640]
    await client.wait_until_ready()
    while not client.is_closed():
        now = datetime.datetime.now()
        nownow = now.replace(second=0, microsecond=0)
        future = now.replace(minute=59, second=0, microsecond=0)
        temp = 0
        if str(nownow) == str(future):
            while temp < len(broadcast_list):
                channel = client.get_channel(broadcast_list[temp])
                req = str(requests.get(api_url, verify=False).content)[3:-2]
                req = req.split(";")
                if req[1] != '':
                    embed = discord.Embed(title=req[0], url=req[1], description=req[2])
                else:
                    embed = discord.Embed(title=req[0], description=req[2])
                await channel.send(embed=embed)
                temp = temp + 1
            await asyncio.sleep(60)
        else:
            await asyncio.sleep(15)
