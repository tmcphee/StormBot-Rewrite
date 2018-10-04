import asyncio
import time
import datetime
import pyodbc
import discord
import sqlite3
import sys
import traceback
import logging
import requests
import os
from os import path
from discord import Game
from discord.ext.commands import Bot
from coco.CocoFunctions import *
from monitor.MemberMonitor import *
from monitor.MessageBroadcast import *
from db.insql import *


def setup_logging_to_file(filename):
    logging.basicConfig(filename=filename, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p')


def extract_function_name():
    tb = sys.exc_info()[-1]
    stk = traceback.extract_tb(tb, 1)
    fname = stk[0][3]
    return fname


def log_exception(e):
    trace_back = sys.exc_info()[2]
    logging.error(
        "Function {function_name} raised {exception_class} ({exception_docstring}): {exception_message} ----- Exception on line ({line})".format(
            function_name=extract_function_name(),  # this is optional
            exception_class=e.__class__,
            exception_docstring=e.__doc__,
            exception_message=e,
            line=trace_back.tb_lineno))


#_sql = mssql()
setup_logging_to_file('StormBot.log')
#CONFIG
text_file = open("StormBot.config", "r")
BOT_CONFIG = text_file.readlines()
text_file.close()

TOKEN = str(BOT_CONFIG[0]).strip()
headers = {}
headers['Api-Key'] = str(BOT_CONFIG[1]).strip()
server_startime = time.time()
'''
retry_flag = True
retry_count = 0
while retry_flag:
    try:
        try:
            conn = pyodbc.connect(
                'DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + server_addr + ';DATABASE=' + database
                + ';UID=' + username + ';PWD=' + password)
            cursor = conn.cursor()
            server_env = 'Linux'
        except:
            conn = pyodbc.connect(
                'DRIVER={SQL SERVER};SERVER=' + server_addr + ';DATABASE=' + database + ';UID=' + username + ';PWD='
                + password)
            cursor = conn.cursor()
            server_env = 'Windows'
        retry_flag = False
        print('Connection to SQL server - Succeeded')
        print('Bot running in ' + str(server_env) + ' environment')
    except Exception as e:
        log_exception(str(e))
        retry_count = retry_count + 1
        time.sleep(2)
        if retry_count == 5:
            print('Connection to SQL server - Failed')
            sys.exit(2)'''

BOT_PREFIX = "?"
client = Bot(command_prefix=BOT_PREFIX)


@client.event
async def on_voice_state_update(member, before, after):
    await voip_tracker(member, before, after)


@client.event
async def on_message(message):
    await message_tracker(client, message)
    # any on_message function should be placed before process_commands
    member = message.author
    if member.guild_permissions.administrator:
        await client.process_commands(message)

@client.event
async def on_member_join(member):
    await member_joined_discord(client, member)


@client.event
async def on_member_remove(member):
    await member_left_discord(client, member)


@client.event
async def on_member_update(before, after):
    await update_member(after, before, after)


@client.event  # 0004
async def on_ready():
    try:
        print("********************************************Login*Details***********************************************")
        print("     Logged in as " + client.user.name)
        print("     Client User ID: " + str(client.user.id))
        print("     Invite at: https://discordapp.com/oauth2/authorize?client_id=" + str(client.user.id) + "&scope=bot")
        print("********************************************************************************************************")
    except Exception as e:
        log_exception(str(e))


async def list_servers():
    try:
        await client.wait_until_ready()
        while not client.is_closed():
            print("********************************************Current*Servers*********************************************")
            for guild in client.guilds:
                print("     " + str(guild.name) + " (Members: " + str(len(guild.members)) + ") [" + str(guild.id) + "]")
            print("********************************************************************************************************")
            await asyncio.sleep(60*60)
    except Exception as e:
        log_exception(str(e))


async def display():
    try:
        await client.wait_until_ready()
        while not client.is_closed():
            await client.change_presence(activity=discord.Game(str(BOT_PREFIX) + "help | V2.0 | BETA"))
            await asyncio.sleep(20)
            await client.change_presence(activity=discord.Game("DEV: ZombieEar | The Woj"))
            await asyncio.sleep(3)
            await client.change_presence(activity=discord.Game(str(BOT_PREFIX) + "help | V2.0 | BETA"))
            await asyncio.sleep(20)
    except Exception as e:
        log_exception(str(e))

''' 
# Begin commands
@client.command(pass_context=True)
async def purge(ctx, clan):
    clan_ids = {
        1: 2926181,
        2: 3089039,
        3: 3092882,
        4: 3143454,
        5: 3208812,
    }
    clan_id = clan_ids.get(int(clan))
    cur = mssql.select(_sql, "select * from clans where ClanId = ?", clan_id)
    rows = cur.fetchall()
    for row in rows:
        print("Purging " + row.ClanName)
        await client.say("Purging " + str(row.ClanName))
        await update_coco_roles(_sql, client, clan_id, str(row.ClanName))


@client.command(pass_conext=True)  # have this function run at least once a week to audit
async def users():
    server_id = '162706186272112640'  # StormBot
    server = client.get_server(server_id)
    for member in server.members:
        mssql.update(_sql, "if not exists(select * from DiscordUsers where DiscordID=?) begin insert into DiscordUsers"
                           " (DiscordID,UserName,Nickname,ServerID) values(?,?,?,?) end",
                     str(member.id), str(member.id), str(member), str(member.display_name), server_id)
        for role in member.roles:
            mssql.update(_sql, "if not exists(select * from DiscordRoles_Users where DiscordID=? and RoleId=?) "
                               "begin insert into DiscordRoles_Users(DiscordID,RoleId) values(?,?) end", str(member.id),
                         str(role.id), str(member.id), str(role.id))
            print(str(role.name))
        print(str(member))
'''


@client.command(pass_context=True)
async def activity(ctx):
    channel = ctx.channel
    message = ctx.message
    content = message.content
    member = ctx.message.author
    mod_ck = moderator_check(member)
    if (mod_ck is True) or member.guild_permissions.administrator:
        s = requests.Session()
        if "<@" in content:
            member_id = str(content[12:-1])
            temp_con = str(content[12:-1])
            if "!" in member_id:
                member_id = temp_con[1:]

            req1 = s.get(
                'https://cococlan.report/api/Discord/' + str(member.guild.id) + '/User/' + str(member_id) + '/Activity/Today'
                , headers=headers)
            user_dat = json.loads(req1.text)
            req2 = s.get(
                'https://cococlan.report/api/Discord/' + str(member.guild.id) + '/User/' + str(member_id) + ''
                , headers=headers)
            get_user = json.loads(req2.text)

            emb = (discord.Embed(title="Activity Request: (" + user_dat[0]['activityDate'] + ")", color=0x49ad3f))
            emb.add_field(name='User', value=get_user[0]['userName'], inline=True)
            emb.add_field(name='User ID', value=user_dat[0]['discordId'], inline=True)
            emb.add_field(name='Nickname/BattleTag', value=get_user[0]['nickName'], inline=True)
            emb.add_field(name='Current Voice Activity', value=user_dat[0]['minutesVoice'], inline=True)
            emb.add_field(name='Current Message Activity', value=user_dat[0]['messagesSent'], inline=True)
            emb.set_footer(text='Requested By: (' + str(member.id) + ') ' + str(member))
            await channel.send(embed=emb)
    else:
        await channel.send('Access Denied - You are not a Moderator or Administrator')
'''

@client.command(pass_context=True)
async def activity(ctx, message):
    print('*' + str(message.content) + '*')
    channel = message.channel
    member = message.author
    mod_ck = moderator_check(member, message.guild)
    if (mod_ck is True) or member.guild_permissions.administrator:
        if "<@" in message:
            member_id = str(message[12:-1])
            print('*' + str(member_id) + '*')
            temp_con = str(message[12:-1])
            if "!" in member_id:
                member_id = temp_con[1:]
                print('*' + str(member_id) + '*')
        else:
            member_id = str(message.author.id)
        temp = mssql.select(_sql, "SELECT * FROM DiscordUsers Join DiscordActivity"
                                  " ON (DiscordUsers.DiscordID = DiscordActivity.DiscordID)"
                                  " WHERE datediff(dd, ActivityDate, getdate()) = 0"
                                  " AND DiscordUsers.DiscordID = ?", member_id)
        user_dat = temp.fetchall()
        if str(user_dat) != '[]':
            emb = (discord.Embed(title="Activity Request:", color=0x49ad3f))
            emb.add_field(name='User', value=user_dat[0][1], inline=True)
            emb.add_field(name='User ID', value=user_dat[0][2], inline=True)
            emb.add_field(name='Nickname/BattleTag', value=user_dat[0][3], inline=True)
            emb.add_field(name='Current Voice Activity', value=user_dat[0][8], inline=True)
            emb.add_field(name='Current Message Activity', value=user_dat[0][9], inline=True)
            emb.add_field(name='Previous 7-Day Activity', value=user_dat[0][5], inline=True)
            emb.set_footer(text='Requested By: (' + str(message.author.id) + ') ' + str(message.author))
            await channel.send(embed=emb)
        else:
            emb = (discord.Embed(title="Activity Request:", color=0x49ad3f))
            emb.set_author(name="Stormbot")
            emb.add_field(name='ERROR - BAD REQUEST',
                          value='That Member don\'t exist. Either the Member is not in the database,'
                                ' you fucked up, '
                                'or the programmer fucked up.', inline=True)
            emb.set_footer(text="If the member exists and the error is repeated please notify ZombieEar#0493 ")
            await channel.send(embed=emb)
    else:
        await channel.send('Access Denied - You are not a Moderator or Administrator')
'''

def fetch_roles(member):
    roles_list_ob = member.roles
    roles_len = len(roles_list_ob)
    if roles_len != 0:
        temp4 = 1
        roles_st = ''
        while temp4 < roles_len:
            roles_st = roles_st + roles_list_ob[temp4].name
            if temp4 >= 1:
                roles_st = roles_st + ','
            temp4 = temp4 + 1
        return roles_st[:-1]
    else:
        return 'NONE'

def moderator_check(member):#check if user is in a Moderator
    try:
        result = False
        mod = 'Moderator'
        programmer = 'Collective Processors'

        roles = fetch_roles(member)

        if mod in roles:
            result = True
        if programmer in roles:
            result = True
        return result
    except Exception as e:
        log_exception(str(e))


client.loop.create_task(list_servers())
client.loop.create_task(display())
#client.loop.create_task(msg_broadcast(client))
client.run(TOKEN, bot=True, reconnect=True)
