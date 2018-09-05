import discord
import asyncio
from random import randint


async def msg_broadcast(client):
    broadcast_list = [384886471531692033, 162706186272112640]
    await client.wait_until_ready()
    while not client.is_closed():
        #await asyncio.sleep(60 * 5)
        temp = 0
        while temp < len(broadcast_list):
            channel = client.get_channel(broadcast_list[temp])
            ran_val = randint(0, 3)
            if ran_val == 0:
                embed = discord.Embed(title="Friendly Reminder (click me!)",
                                      url="https://www.bungie.net/en/Forums/Post/248172496",
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
                                      description="If you are going to be gone for awhile or jsut stepping out for a "
                                                  "few days please let a staff member know. If you let us know before "
                                                  "hand you will be given 1 extra week before demotions start and "
                                                  "eventually kick. We understand that life gets in the way and event "
                                                  "come up, we are here to help you when those do happen. Please be "
                                                  "sure to let a staff member know of your absense and no need to "
                                                  "stress about it.")
            if ran_val == 3:
                embed = discord.Embed(title="Looking for raid help?",
                                      description="Feel free to @Sherpa if you're looking to learn or improve on any "
                                                  "of the raids!")
            await channel.send(embed=embed)
            temp = temp + 1
        await asyncio.sleep(60 * 60)