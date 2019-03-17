import asyncio
import time
import discord
import requests
import datetime

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

text_file = open("StormBot.config", "r")
BOT_CONFIG = text_file.readlines()
text_file.close()

key = str(BOT_CONFIG[1]).strip()
api_url = str(BOT_CONFIG[2]).strip()


async def voip_tracker(member, before, after):
    blocked_voip = [478428670332239873, 501218568151498754, 382125277066690562, 381910672256008196, 409383273182003211]
    # if not member.guild_permissions.administrator:
        # return
    if str(after.channel) == 'None':
        return
    if after.channel.id not in blocked_voip:
        if str(before.channel) != str(after.channel):
            tempb = str(before.channel)
            tempa = str(after.channel)
            start = int(time.time())
            while str(before.channel) != str(after.channel):
                if after.channel is None:
                    break
                if after.channel.id in blocked_voip or str(before.channel) != tempb or str(after.channel) != tempa:
                    break
                await asyncio.sleep(1)
            duration = ((int(time.time()) - start) / 60)
            try:
                send_url = api_url + "/API/VoipTracker.php?id=" + str(key) + "&UserName=" +\
                          str(member) + "&DiscordID=" + str(member.id) + "&Nickname=" + str(member.nick) + "&Duration="\
                          + str(duration) + "&ServerID=" + str(member.guild.id) + ""
                modified_url = send_url.replace("#", "<>", 3)
                requests.get(modified_url, verify=False)
            except Exception as e:
                print(str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M %p %Z")) + " -- [" + str(member.guild.id) + "] -> ERROR: " + str(e) +
                      " --> Trying again in 5 seconds")
                await asyncio.sleep(5)
                send_url = api_url + "/API/VoipTracker.php?id=" + str(key) + "&UserName=" + \
                           str(member) + "&DiscordID=" + str(member.id) + "&Nickname=" + str(member.nick) + "&Duration=" \
                           + str(duration) + "&ServerID=" + str(member.guild.id) + ""
                modified_url = send_url.replace("#", "<>", 3)
                requests.get(modified_url, verify=False)


async def message_tracker(client, message):
    blocked_channels = ['162706186272112640']
    server = message.guild
    member = message.author
    if message.author == client.user:  # do not want the bot to reply to itself
        return
    send_url = api_url + "/API/MessageTracker.php?id=" + str(key) + "&UserName=" + \
            str(member) + "&DiscordID=" + str(member.id) + "&Nickname=" + str(member.nick) + "&ServerID="\
            + str(member.guild.id) + ""
    modified_url = send_url.replace("#", "<>", 3)
    requests.get(modified_url, verify=False)


async def member_joined_discord(client, member):
    await add_member_database(member)
    if member.guild.id == 162706186272112640:
        embed = discord.Embed(title="Welcome to Collective Conscious.",
                              description="CoCo is a PC-only Destiny 2 clan covering both NA and EU.", color=0x008000)
        embed.add_field(name='1. Server nickname',
                        value='Your nickname must match your BattleTag regardless of clan member status.\n'
                              'Example: PeachTree#11671',
                        inline=False)
        embed.add_field(name='2. Clan Applications',
                        value='Head to the #clan-application channel and apply to one of '
                        'the clans showing as "recruiting." Once you\'ve requested '
                        'membership, post in #request-a-rank stating the clan you '
                        'applied to and clan staff will process your request.',
                        inline=False)
        embed.add_field(name='3. Clan & Discord Information',
                        value='Please take a moment to read over server rules '
                        'in #rules as well as Frequently Asked Questions '
                        'in #faq before asking questions, as you may find '
                        'them answered!', inline=False)
        embed.set_footer(text='I\'m a bot. If you have questions, please contact a Clan Leader, Admin, or Moderator!')
        await member.send(embed=embed)
        print(str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M %p %Z")) + " -- [" + str(member.guild.id) + "] -> Issued Join message to " + str(member))


async def member_left_discord(client, member):
    print(str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M %p %Z")) + " -- [" + str(member.guild.id) + "] -> MEMBER *" + str(member) + "* Has Left Discord - Removing user from DataBase")
    send_url = api_url + "/API/RemoveMember.php?id=" + str(key) + "&DiscordID=" + str(member.id) \
               + "&ServerID=" + str(member.guild.id) + ""
    modified_url = send_url.replace("#", "<>", 3)
    requests.get(modified_url, verify=False)


async def update_member(member, before, after):
    if before.nick != after.nick:
        send_url = api_url + "/API/UpdateNickname.php?id=" + str(key) + "&UserName=" + \
                   str(member) + "&DiscordID=" + str(member.id) + "&Nickname=" + str(member.nick) + "&ServerID=" \
                   + str(member.guild.id) + ""
        modified_url = send_url.replace("#", "<>", 3)
        requests.get(modified_url, verify=False)

    # UPDATE ROLES
    '''new_roles = ""
    if before.roles != after.roles:
        for role in before.roles:
            gc_roles_url = "https://cococlan.report/api/Discord/" + str(member.guild.id) + "/User/" \
                           + str(after.id) + "/Roles/" + str(role.id) + "/Update"
            s.get(gc_roles_url, headers=headers)
        for role in after.roles:
            new_roles += role.name + ", "
            ins_roles_url = "https://cococlan.report/api/Discord/" + str(member.guild.id) + "/User/" \
                            + str(after.id) + "/Roles/" + str(role.id) + "/Add"
            s.get(ins_roles_url, headers=headers)
        print("Update roles for " + str(member.nick) + " to " + new_roles)
'''
    if str(before) != str(after):
        send_url = api_url + "/API/UpdateMember.php?id=" + str(key) + "&UserName=" + \
                   str(member) + "&DiscordID=" + str(member.id) + "&Nickname=" + str(member.nick) + "&ServerID=" \
                   + str(member.guild.id) + ""
        requests.get(send_url, verify=False)


async def add_member_database(member):
    print(str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M %p %Z")) + " -- [" + str(member.guild.id) + "] -> MEMBER *" + str(member) + "* NOT FOUND - Adding user to DataBase")
    send_url = api_url + "/API/AddMember.php?id=" + str(key) + "&UserName=" + \
              str(member) + "&DiscordID=" + str(member.id) + "&Nickname=" + str(member.nick) + "&ServerID=" \
              + str(member.guild.id) + ""
    modified_url = send_url.replace("#", "<>", 3)
    requests.get(modified_url, verify=False)

