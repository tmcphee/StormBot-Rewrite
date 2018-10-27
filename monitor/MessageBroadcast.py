import discord
import asyncio
import time
import datetime
from random import randint
from random import seed
TOTAL_BROADCASTS = 6    # length


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
                seed(time.time())
                channel = client.get_channel(broadcast_list[temp])
                ran_val = randint(0, TOTAL_BROADCASTS)
                if ran_val == 0:
                    embed = discord.Embed(title="Friendly Reminder (click me!)",
                                          url="https://www.bungie.net/en/Forums/Post/248172496",
                                          description="If you want to help the community, then saying hi on our Bungie"
                                                      " posts, and up-voting them really makse a big difference! (New"
                                                      " ones are made weekly). Big shoutout to everyone who commented "
                                                      "and up voted last week's post. We're really feeling the love <3")
                if ran_val == 1:
                    embed = discord.Embed(title="Friendly Reminder",
                                          description="Frequenter and Veteran are just ways that we show our love for"
                                                      " you being apart of this community. They grant you additional"
                                                      " weeks before being kicked from a clan. We know that life"
                                                      " happens, and, we'd never want to kick our friends. You"
                                                      " effectively have 4 weeks if you get veteran, 1 week for each"
                                                      " role (Veteran, Frequenter, Clan Member, Low Activity).")
                if ran_val == 2:
                    embed = discord.Embed(title="Friendly Reminder",
                                          description="If you are going to be gone for a while, or just stepping out"
                                                      " for a few days, please let a staff member know. If you let us"
                                                      " know before hand, you will be given 1 extra week before"
                                                      " demotions start; including being kicked. We understand that"
                                                      " life gets in the way and events come up. We are here to help"
                                                      " you when things happen. Please be sure to let a staff member"
                                                      " know of your absence, and there will be no need to stress"
                                                      " about it.")
                if ran_val == 3:
                    embed = discord.Embed(title="Looking for raid help?",
                                          description="Feel free to @Sherpa if you're looking to learn or improve on"
                                                      " any of the raids!")
                if ran_val == 4:
                    embed = discord.Embed(title="Friendly Reminder",
                                          description="CoCo Clan Members have exclusive access to Clan Game nights"
                                                      " hosted regularly every week! If you haven't already; Hop over"
                                                      " to #role-assignments and click on the GREEN Check mark under"
                                                      " the Game Night prompt to receive notifications on when game"
                                                      " nights are happening as well as what game is being played"
                                                      " for the week!")
                if ran_val == 5:
                    embed = discord.Embed(title="Friendly Reminder",
                                          description="Please remember to change your discord server name,"
                                                      " it's a requirement of the discord!")
                # if ran_val == 6:
                #     embed = discord.Embed(title="Recruiting Python Programmer",
                #                           description="Are you a programmer and looking to help improve the CoCo"
                #                                       " Clan community. ZombieEar is currently seeking someone with"
                #                                       " python knowledge to help improve StormBot. If this interests"
                #                                       " you please DM @ZombieEar")
                if ran_val == 6:
                    embed = discord.Embed(title="Recruiting Web Developer",
                                          description="Are you a web developer and looking to help improve the CoCo"
                                                      " Clan community? Woj is currently seeking someone with"
                                                      " knowledge of css and html to help create CoCo's first clan" 
                                                      " website. If this interests you please DM @dasWoj#1113")
                await channel.send(embed=embed)
                temp = temp + 1
            await asyncio.sleep(60)
        else:
            await asyncio.sleep(15)
