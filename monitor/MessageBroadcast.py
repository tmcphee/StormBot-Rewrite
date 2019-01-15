import discord
import asyncio
import time
import datetime
from random import randint
from random import seed
import requests
import json
import sys
# TOTAL_BROADCASTS = 5    # length

text_file = open("StormBot.config", "r")
BOT_CONFIG = text_file.readlines()
text_file.close()
headers = {}
headers['Api-Key'] = str(BOT_CONFIG[1]).strip()


def _get_coco_response(api_call):
    retry_flag = True
    retry_count = 0
    coco_url = "https://cocogamers.com/"
    while retry_flag:
        try:
            s = requests.Session()
            req = s.get(coco_url + api_call, headers=headers)
            json_ret = json.loads(req.text)
            return json_ret
        except Exception as e:
            print(str(e))
            print('API Error: Retrying response after 2 second')
            retry_count += 1
            time.sleep(2)
            if retry_count == 10:
                sys.exit(2)


async def msg_broadcast(client):
    # Will post random broadcast in each of the channel ID's in this list
    message_url = "api/Discord/GetStormBotMessages"
    res = _get_coco_response(message_url)
    total_broadcasts = len(res)
    print(res)
    print(total_broadcasts)
    broadcast_list = [384886471531692033, 162706186272112640]
    await client.wait_until_ready()
    while not client.is_closed():
        now = datetime.datetime.now()
        nownow = now.replace(second=0, microsecond=0)
        future = now.replace(minute=59, second=0, microsecond=0)
        temp = 0
        if str(nownow) == str(future):
            while temp < len(broadcast_list):
                seed(time.time())
                channel = client.get_channel(broadcast_list[temp])
                ran_val = randint(1, total_broadcasts)
                message_number = 0
                for message in res:
                    message_number += 1
                    if message_number == ran_val:
                        if len(message['url']) > 0:
                            embed = discord.Embed(title=message['title'], url=message['url'],
                                                  description=message['description'])
                        else:
                            embed = discord.Embed(title=message['title'], description=message['description'])
                await channel.send(embed=embed)
                temp = temp + 1
            await asyncio.sleep(60)
        else:
            await asyncio.sleep(15)
