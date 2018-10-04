import json
import requests
import asyncio
from coco.CocoFunctions import *

text_file = open("StormBot.config", "r")
BOT_CONFIG = text_file.readlines()
text_file.close()
headers = {}
headers['Api-Key'] = str(BOT_CONFIG[1]).strip()


async def voip_tracker(member, before, after):
    blocked_voip = ['381910672256008196', '409383273182003211', '463518519556833280', '382125277066690562']
    if str(after.channel) == 'None':
        return
    if str(after.channel.id) not in blocked_voip:
        curr_channel = str(after.channel)
        before_channel = str(before.channel)
        if after.channel is not None:
            start = int(time.time())
            while str(before.channel) == before_channel and str(after.channel) == curr_channel:
                await asyncio.sleep(0.5)
            finish = int(time.time())
            duration = ((finish - start) / 60)
            s = requests.Session()
            req1 = s.get(
                'https://cococlan.report/api/Discord/' + str(member.guild.id) + '/User/' + str(member.id) + ''
                , headers=headers)
            get_user = json.loads(req1.text)
            if get_user is []:
                add_member_database(after)
            req2 = s.get(
                'https://cococlan.report/api/Discord/' + str(member.guild.id) + '/User/' + str(member.id) +
                '/Activity/Today'
                , headers=headers)
            get_activity = json.loads(req2.text)
            if get_activity == []:
                s.get(
                    'https://cococlan.report/api/Discord/' + str(member.guild.id) + '/User/' + str(member.id) +
                    '/InsertActivity/' + str(1) + '/' + str(int(duration)) + ''
                    , headers=headers)
            else:
                s.get(
                    'https://cococlan.report/api/Discord/' + str(member.guild.id) + '/User/' + str(member.id) +
                    '/UpdateActivity/' + str(1) + '/' + str(int(duration)) + ''
                    , headers=headers)
            return


async def message_tracker(client, message):
    blocked_channels = ['162706186272112640']
    server = message.guild
    sender = server.get_member(message.author.id)
    if message.author == client.user:  # do not want the bot to reply to itself
        return
    s = requests.Session()
    req1 = s.get('https://cococlan.report/api/Discord/' + str(message.guild.id) + '/User/' + str(message.author.id) + ''
                , headers=headers)
    get_user = json.loads(req1.text)
    if get_user is []:
        add_member_database(sender)
    req2 = s.get('https://cococlan.report/api/Discord/' + str(message.guild.id) + '/User/' + str(message.author.id) +
                 '/Activity/Today'
                 , headers=headers)
    get_activity = json.loads(req2.text)
    if get_activity == []:
        s.get('https://cococlan.report/api/Discord/' + str(message.guild.id) + '/User/' + str(message.author.id) +
                 '/InsertActivity/'+ str(0) + '/' + str(1) + ''
              , headers=headers)
    else:
        s.get('https://cococlan.report/api/Discord/' + str(message.guild.id) + '/User/' + str(message.author.id) +
              '/UpdateActivity/' + str(0) + '/' + str(1) + ''
              , headers=headers)


async def member_joined_discord(client, member):
    await add_member_database(member)
    embed = discord.Embed(title="Welcome to Collective Conscious.",
                          description="CoCo is a PC-only Destiny 2 clan covering both NA and EU.", color=0x008000)
    embed.add_field(name='1. Server nickname',
                    value='Your nickname must match your BattleTag regardless of clan member status.\n'
                          'Example: PeachTree#11671\n Set your nickname using the command \'?change_nick BattleTag\'.',
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
    print("-on_member_join      User Joined      User:" + str(member))


async def member_left_discord(client, member):
    print('')


async def update_member(member, before, after):
    s = requests.Session()
    req1 = s.get(
        'https://cococlan.report/api/Discord/' + str(member.guild.id) + '/User/' + str(after.id) + ''
        , headers=headers)
    get_user = json.loads(req1.text)
    if before.nick != after.nick:
        if get_user == []:
            await add_member_database(after)
        else:
            s.get('https://cococlan.report/api/Discord/' + str(member.guild.id) + '/User/' + str(after.id) +
                  '/UpdateNickname/' + str(after.nick) + ''
                  , headers=headers)
            print("-Updated the user: " + str(after.name) + " changed Nickname from *" + str(before.nick) + "* to *"
                  + str(after.nick) + "*")
    '''if before.roles != after.roles:
        if len(retn) == 0:
            add_member_database(after)
        roles_arr = fetch_roles(after)
        temp = 0
        while temp < len(roles_arr):
            mssql.update(_sql, "if not exists(select * from DiscordRoles_Users where DiscordID=? and RoleId=?) "
                               "begin insert into DiscordRoles_Users(DiscordID,RoleId) values(?,?) end", str(after.id),
                         str(roles_arr[temp].id), str(after.id), str(roles_arr[temp].id))
            temp += 1
        sel = mssql.select(_sql, "SELECT * FROM DiscordRoles_Users WHERE DiscordID = ?", str(after.id))
        retn2 = sel.fetchall()
        temp2 = 0
        temp3 = 0
        while temp2 < len(retn2):
            while temp3 < len(roles_arr):
                if retn2[temp2][1] != roles_arr[temp3].id:
                    mssql.update(_sql, "Update DiscordRoles_Users"
                                       " SET GCRecord = ?"
                                       " Where DiscordID=? and RoleId=?) "
                                 , int(datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d')), str(after.id)
                                 , str(roles_arr[temp3].id))
                temp3 += 1
            temp2 += 1'''
    if str(before) != str(after):
        if get_user == []:
            await add_member_database(after)
        else:
            s.get('https://cococlan.report/api/Discord/' + str(member.guild.id) + '/User/' + str(after.id) +
                  '/UpdateNamee/' + str(after) + ''
                  , headers=headers)
            print("-Updated the user: " + str(after.id) + " changed Username from  *" + str(before) + "* to *"
                  + str(after) + "*")


async def add_member_database(member):
    print("Warning 0012 -- MEMBER *" + str(member) + "* NOT FOUND - Adding user to DataBase")
    s = requests.Session()
    s.get('https://cococlan.report/api/Discord/' + str(member.guild.id) + '/User/' + str(member.id) +
          '/AddUser/' + str(member) + '/' + str(member.nick) + ''
          , headers=headers)
