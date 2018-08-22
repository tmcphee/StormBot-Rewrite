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

BOT_PREFIX = "?"
client = Bot(command_prefix=BOT_PREFIX)


@client.event
async def on_message(message):
    # any on_message function should be placed before process_commands
    await client.process_commands(message)


@client.event  # 0004
async def on_ready():
    try:
        await client.change_presence(game=Game(name="TESTING - IN DEVELOPMENT"))#?help
        print("********************************************Login*Details***********************************************")
        print("     Logged in as " + client.user.name)
        print("     Client User ID: " + client.user.id)
        print("     Invite at: https://discordapp.com/oauth2/authorize?client_id=" + client.user.id + "&scope=bot")
        print("********************************************************************************************************")
    except Exception as e:
        log_exception(str(e))


async def list_servers():
    try:
        await client.wait_until_ready()
        while not client.is_closed:
            print("********************************************Current*Servers*********************************************")
            for server in client.servers:
                print("     " + str(server.name) + " (Members: " + str(len(server.members)) + ") [" + str(server.id) + "]")
            print("********************************************************************************************************")
            await asyncio.sleep(60*60)
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
    for row in cur:
        print(row.ClanName)
        await client.say("Purging " + str(row.ClanName))
        await update_coco_roles(_sql, client, clan_id)


client.run(TOKEN)
