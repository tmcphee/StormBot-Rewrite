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
from odbc.mssql import *
from coco.CocoFunctions import *
from monitor.MemberMonitor import *


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


_sql = mssql()
setup_logging_to_file('StormBot_log.txt')
#CONFIG
text_file = open("StormBot.config", "r")
BOT_CONFIG = text_file.readlines()
text_file.close()

server_addr = str(BOT_CONFIG[0]).strip()
database = str(BOT_CONFIG[1]).strip()
username = str(BOT_CONFIG[2]).strip()
password = str(BOT_CONFIG[3]).strip()
TOKEN = str(BOT_CONFIG[4]).strip()
server_startime = time.time()

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
            sys.exit(2)

SQL = path.exists("pythonsqlite.db")  # Resumes or creates Database file
if SQL is True:
    print("SQL INTERNAL SERVER -- DATABASE RESUMING TO SAVED STATE")
    connect = sqlite3.connect('pythonsqlite.db')
    cursor2 = connect.cursor()
else:
    print("WARNING -- INTERNAL DATABASE FAILED TO RESUME TO SAVED STATE")
    print("        -- SYSTEM CREATING DATABASE WITH NEW TABLE")
    connect = sqlite3.connect('pythonsqlite.db')
    cursor2 = connect.cursor()
    cursor2.execute("""CREATE TABLE Presets
                          (NoVoice integer , NoMessages integer, GuestRole text, ActiveRole text, InactiveRole text, 
                          BeginDate text, StombotChannel text)
                       """)
    connect.commit()
    cursor2.execute("""INSERT INTO Presets VALUES (?,?,?,?,?,?,?)""", (120, 10, "381911719901134850",
                                                                       "[TEST]Discord Active", "[TEST]Discord Inactive",
                                                                       '2018-08-05 20:59:08', '2018-08-05 20:59:08'))
    connect.commit()
    cursor2.execute("""CREATE TABLE Fun
                              (joke text , insult text)
                           """)
    connect.commit()
    cursor2.execute("""INSERT INTO Fun VALUES (?,?)""", ('on', 'on'))
    connect.commit()

BOT_PREFIX = "!"
client = Bot(command_prefix=BOT_PREFIX)


@client.event
async def on_voice_state_update(before, after):
    await voip_tracker(_sql, before, after)


@client.event
async def on_message(message):
    await message_tracker(_sql, client, message)
    # any on_message function should be placed before process_commands
    await client.process_commands(message)


@client.event
async def on_member_join(member):
    await member_joined_discord(_sql, client, member)


@client.event
async def on_member_remove(member):
    await member_left_discord(client, member)


@client.event
async def on_member_update(before, after):
    await update_member(_sql, before, after)


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
    except Exception as e:
        log_exception(str(e))

        
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

        
client.loop.create_task(list_servers())
client.loop.create_task(display())
client.run(TOKEN, bot=True, reconnect=True)
