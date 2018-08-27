import discord
import asyncio
from random import randint
from odbc.mssql import *


async def msg_broadcast(client):
    broadcast_list = ['384886471531692033', '162706186272112640']
    await client.wait_until_ready()
    while not client.is_closed:
        temp = 0
        while temp < len(broadcast_list):
            ran_val = randint(0, 2)
            if ran_val == 0:
                embed = discord.Embed(title="Friendly Reminder (click me!)",
                                      url="https://www.bungie.net/en/Forums/Post/248075442",
                                      description="If you want to help the community, then saying hi on our advert post, "
                                                  "and giving it a thumbs up really does make a big difference! (New one "
                                                  "made weekly). Big shoutout to everyone who commented and thumbs uped "
                                                  "last weeks post. We're really feeling the love <3")
            if ran_val == 1:
                embed = discord.Embed(title="Friendly Reminder",
                                      description="Frequenter and Veteran are just ways that we show our love for you "
                                                  "being apart of this (you da best! <3). It gives you another week "
                                                  "before a kick (Just because we know that shit happens, life likes "
                                                  "to throw lemons (I HATE LEMONS!). And, we'd never want to kick our "
                                                  "friends. (You effectively have 4 weeks if you get veteran, 1 week "
                                                  "for each role (Veteran, Frequenter, Clan Member, Low Activity))")
            if ran_val == 2:
                embed = discord.Embed(title="Friendly Reminder",
                                      description="If you're going to be gone for a while (plz alert staff). "
                                                  "The normal course of action is to give you 1 week freebie. Then "
                                                  "to start demotions; to eventual kick (We get that life get's in "
                                                  "the way (GET OUT OF MY WAY LIFE, I'VE HAD IT UP TO HERE WITH YOU!!). "
                                                  "And, we want to show that, we understand mange. We get it, don't "
                                                  "sweat it (sick rhymes tho?))")
            await client.send_message(client.get_channel(broadcast_list[temp]), embed=embed)
            temp = temp + 1
        #await client.send_message(client.get_channel('384886471531692033'), embed=embed)
        #await client.send_message(client.get_channel('162706186272112640'), embed=embed)
        await asyncio.sleep(60 * 60)