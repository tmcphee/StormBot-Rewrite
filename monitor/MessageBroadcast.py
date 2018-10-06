import discord
import asyncio
import time
import datetime
from random import randint
from random import seed
TOTAL_BROADCASTS = 3


async def msg_broadcast(client):
    # Will post random broadcast in each of the channel ID's in this list
    broadcast_list = [384886471531692033, 162706186272112640]
    await client.wait_until_ready()
    while not client.is_closed():
        now = datetime.datetime.now()
        future = datetime.datetime.now().replace(minute=59)
        temp = 0
        seed(time.time())
        if now == future:
            while temp < len(broadcast_list):
                channel = client.get_channel(broadcast_list[temp])
                ran_val = randint(0, TOTAL_BROADCASTS)
                if ran_val == 0:
                    embed = discord.Embed(title="Friendly Reminder (click me!)",
                                          url="https://www.bungie.net/en/Forums/Post/248172496",
                                          description="If you want to help the community, then saying hi on our Bungie posts, "
                                                      "and up-voting them really makse a big difference! (New ones "
                                                      "are made weekly). Big shoutout to everyone who commented and up voted "
                                                      "last week's post. We're really feeling the love <3")
                if ran_val == 1:
                    embed = discord.Embed(title="Friendly Reminder",
                                          description="Frequenter and Veteran are just ways that we show our love for you "
                                                      "being apart of this community. They grant you additional weeks "
                                                      "before being kicked from a clan. We know that life happens, "
                                                      "and, we'd never want to kick our "
                                                      "friends. You effectively have 4 weeks if you get veteran, 1 week "
                                                      "for each role (Veteran, Frequenter, Clan Member, Low Activity).")
                if ran_val == 2:
                    embed = discord.Embed(title="Friendly Reminder",
                                          description="If you are going to be gone for a while, or just stepping out for a "
                                                      "few days, please let a staff member know. If you let us know before "
                                                      "hand, you will be given 1 extra week before demotions start; including "
                                                      "being kicked. We understand that life gets in the way and events "
                                                      "come up. We are here to help you when things happen. Please be "
                                                      "sure to let a staff member know of your absence, and there will "
                                                      "be no need to stress about it.")
                if ran_val == 3:
                    embed = discord.Embed(title="Looking for raid help?",
                                          description="Feel free to @Sherpa if you're looking to learn or improve on any "
                                                      "of the raids!")
                await channel.send(embed=embed)
                temp = temp + 1
                await asyncio.sleep(60)
        else:
            await asyncio.sleep(30)
