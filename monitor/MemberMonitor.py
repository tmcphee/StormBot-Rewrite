import discord
import time
import datetime
import asyncio
from odbc.mssql import *
from coco.CocoFunctions import *

discord_users = 'DiscordUsers'
discord_activity = 'DiscordActivity'


async def voip_tracker(before, after):
    blocked_voip = ['381910672256008196', '409383273182003211', '463518519556833280', '382125277066690562']
    if str(after.voice.voice_channel.id) not in blocked_voip:
        if before.voice.voice_channel is None and after.voice.voice_channel is not None:
            start = int(time.time())
            while before.voice.voice_channel is None and after.voice.voice_channel is not None:
                await asyncio.sleep(0.5)
            finish = int(time.time())
            duration = ((finish - start) / 60)
            temp = mssql.select("""SELECT * FROM DiscordUsers WHERE DiscordID = ?""", (str(after.id),))
            retn = temp.fetchall()
            # print(str(after) + '    Time:' + str(duration))
            if len(retn) == 0:
                print("Warning 0008 -- MEMBER *" + str(after) + "* NOT FOUND - Adding user to DataBase")
                add_member_database(after)
                mssql.update("""INSERT INTO DiscordActivity VALUES (?, ?, 0)""",
                            (str(after.id), int(duration)))
            else:
                sql = """
                                       UPDATE DiscordActivity
                                       SET VOIP = VOIP + ?
                                       WHERE User_ID = ?
                                    """
                data = (duration, str(after.id))
                mssql.update(sql, data)


async def message_tracker(_sql, client, message):
    blocked_channels = ['162706186272112640']
    server = message.guild.id
    sender = server.get_member(message.author.id)
    if message.author == client.user:  # do not want the bot to reply to itself
        return

    author = str(message.author)
    temp2 = mssql.select("""SELECT * FROM DiscordActivity WHERE User_ID = ?""", (message.author.id,))
    retn = temp2.fetchone()
    if retn is None:
        member2 = server.get_member(message.author.id)
        usr_roles2 = fetch_roles(member2)
        print("Warning 0007 -- MEMBER *" + str(author) + "* NOT FOUND - Adding user to DataBase")
        mssql.update("""INSERT INTO DiscordActivity VALUES (?, ?, ?, 0, 1, 0, 'NA', 'NA', ?)""",
                    (author, str(message.author.id)
                     , str(message.author.display_name), usr_roles2))
    else:
        sql = "UPDATE DiscordActivity" \
              " SET Messages_Sent = Messages_Sent + ?" \
              " WHERE User_ID = ?"
        data = (1, str(message.author.id))
        mssql.update(sql, data)


async def member_joined_discord(client, member):
    add_member_database(member)
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
    await client.send_message(member, embed=embed)
    print("-on_member_join      User Joined      User:" + str(member))


async def member_left_discord(client, member):
    print('')


async def update_member(_sql, before, after):
    temp = mssql.select(_sql, "SELECT * FROM DiscordUsers WHERE DiscordID = ?", str(after.id))
    retn = temp.fetchall()
    if before.nick != after.nick:
        if len(retn) == 0:
            await add_member_database(after)
        else:
            query = """
                               UPDATE DiscordUsers
                               SET Nickname = ?
                               WHERE DiscordID = ?
                            """
            data = (str(after.nick), str(after.id))
            mssql.update(query, data)
            print("-Updated the user: " + after.name + " changed Nickname from *" + str(before.nick) + "* to *"
                  + str(after.nick) + "*")
    if before.roles != after.roles:
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
            temp2 += 1
    if str(before) != str(after):
        if len(retn) == 0:
            await add_member_database(after)
        else:

            sql = """
                               UPDATE DiscordUsers
                               SET UserName = ?
                               WHERE DiscordID = ?
                            """
            data = (str(after), str(after.id))
            mssql.update(sql, data)
            print("-Updated the user: " + after.id + " changed Username from  *" + str(before) + "* to *"
                  + str(after) + "*")


async def add_member_database(member):
    print("Warning 0012 -- MEMBER *" + str(member) + "* NOT FOUND - Adding user to DataBase")
    mssql.select("""INSERT INTO DiscordUsers VALUES (?, ?, ?, ?)""",
                (str(member), str(member.id), str(member.nick), str(member.guild.id)))
