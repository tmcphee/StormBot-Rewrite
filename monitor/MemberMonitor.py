import asyncio
import time
import discord
import datetime
from db import *

_sql = mssql()

text_file = open("StormBot.config", "r")
BOT_CONFIG = text_file.readlines()
text_file.close()


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
            get_user = mssql.select(_sql, "SELECT * FROM DiscordUsers WHERE DiscordID = ? and ServerID = ?", str(member.id), member.guild.id)
            if get_user is 'None':
                await add_member_database(after)
            get_activity = mssql.select(_sql, "SELECT * FROM DiscordActivity WHERE DiscordID = ? and ServerID = ?"
                                              " and datediff(dd, ActivityDate, getdate()) = 0"
                                        , str(member.id), member.guild.id)
            rows = get_activity.fetchall()
            if rows == []:
                mssql.update(_sql, "INSERT INTO DiscordActivity VALUES (?, ?, ?, ?, ?)",
                             str(member.id), int(duration), 0, member.guild.id
                             , datetime.datetime.now())
            else:
                query = "UPDATE DiscordActivity" \
                        " SET Minutes_Voice = Minutes_Voice + ?" \
                        " WHERE DiscordID = ? and datediff(dd, ActivityDate, getdate()) = 0"
                mssql.update(_sql, query, duration, str(member.id))


async def message_tracker(client, message):
    blocked_channels = ['162706186272112640']
    server = message.guild
    sender = message.author
    if message.author == client.user:  # do not want the bot to reply to itself
        return
    get_user = mssql.select(_sql, "SELECT * FROM DiscordUsers WHERE DiscordID = ? and ServerID = ?", str(sender.id), sender.guild.id)
    if get_user is 'None':
        await add_member_database(sender)
    get_activity = mssql.select(_sql, "SELECT * FROM DiscordActivity WHERE DiscordID = ? and ServerID = ? and "
                                      "datediff(dd, ActivityDate, getdate()) = 0"
                                , str(sender.id), sender.guild.id)
    rows = get_activity.fetchall()
    if rows == []:
        mssql.update(_sql, "INSERT INTO DiscordActivity VALUES (?, ?, ?, ?, ?)",
                     str(sender.id), 0, 1, message.guild.id
                     , datetime.datetime.now())
    else:
        query = "UPDATE DiscordActivity" \
                " SET Messages_Sent = Messages_Sent + ?" \
                " WHERE DiscordID = ? and ServerID = ? and datediff(dd, ActivityDate, getdate()) = 0"
        mssql.update(_sql, query, 1, str(sender.id), sender.guild.id)


async def member_joined_discord(client, member):
    await add_member_database(member)
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
    print("-on_member_join      User Joined      User:" + str(member))


async def member_left_discord(client, member):
    print('')


async def update_member(member, before, after):
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
            mssql.update(_sql, query, data)
            print("-Updated the user: " + after.name + " changed Nickname from *" + str(before.nick) + "* to *"
                  + str(after.nick) + "*")

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
    mssql.select(_sql, "INSERT INTO DiscordUsers VALUES (?, ?, ?, ?, ?)"
                 , str(member), str(member.id), str(member.nick), member.guild.id, 0)

