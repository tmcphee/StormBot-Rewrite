import datetime
import sys
import traceback
import logging
from discord.ext.commands import Bot
from monitor.MemberMonitor import *
from monitor.MessageBroadcast import *
from instance.main import *
systemstart = int(time.time())


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
APIKEY = str(BOT_CONFIG[1]).strip()
headers['Api-Key'] = APIKEY
server_startime = time.time()

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
                'https://cococlan.report/api/Discord/' + str(member.guild.id) + '/User/' + str(member_id) + '/Activity'
                , headers=headers)
            user_dat = json.loads(req1.text)

            emb = (discord.Embed(title="Activity Request:", color=0x49ad3f))
            emb.add_field(name='User', value=user_dat[0]['userName'], inline=True)
            emb.add_field(name='User ID', value=user_dat[0]['discordId'], inline=True)
            emb.add_field(name='Nickname/BattleTag', value=user_dat[0]['nickName'], inline=True)
            emb.add_field(name='Current Voice Activity', value=user_dat[0]['voip'], inline=True)
            emb.add_field(name='Current Message Activity', value=user_dat[0]['totalMessage'], inline=True)
            emb.set_footer(text='Requested By: (' + str(member.id) + ') ' + str(member))
            await channel.send(embed=emb)
    else:
        await channel.send('Access Denied - You are not a Moderator or Administrator')


@client.command(pass_context=True)
async def activitys(ctx):
    channel = ctx.channel
    message = ctx.message
    content = message.content
    member = ctx.message.author
    contents = content.split()

    mod_ck = moderator_check(member)
    if (mod_ck is True) or member.guild_permissions.administrator:
        startdate = str(contents[2]).split('-')
        datetimestart = datetime.datetime.now().replace(month=int(startdate[0]), day=int(startdate[1]),
                                                        year=(2000 + int(startdate[2])), hour=0, minute=0,
                                                        second=0)
        enddate = str(contents[3]).split('-')
        datetimeend = datetime.datetime.now().replace(month=int(enddate[0]), day=int(enddate[1]),
                                                      year=int(2000 + int(enddate[2])), hour=23, minute=59,
                                                      second=59)
        s = requests.Session()
        if "<@" in content:
            member_id = str(contents[1][2:-1])
            if "!" in member_id:
                member_id = member_id[1:]

            req1 = s.get(
                'https://cococlan.report/api/Discord/' + str(member.guild.id) + '/User/' + str(member_id) + '/Activity/'
                + str(datetimestart) + "/" + str(datetimeend), headers=headers)
            user_dat = json.loads(req1.text)

            emb = (discord.Embed(title="Activity Request:", color=0x49ad3f))
            emb.add_field(name='User', value=user_dat[0]['userName'], inline=True)
            emb.add_field(name='User ID', value=user_dat[0]['discordId'], inline=True)
            emb.add_field(name='Nickname/BattleTag', value=user_dat[0]['nickName'], inline=True)
            emb.add_field(name='Current Voice Activity', value=user_dat[0]['voip'], inline=True)
            emb.add_field(name='Current Message Activity', value=user_dat[0]['totalMessage'], inline=True)
            emb.add_field(name='Start Date', value=user_dat[0]['startDate'], inline=True)
            emb.add_field(name='End Date', value=user_dat[0]['endDate'], inline=True)
            emb.set_footer(text='Requested By: (' + str(member.id) + ') ' + str(member))
            await channel.send(embed=emb)
    else:
        await channel.send('Access Denied - You are not a Moderator or Administrator')


@client.command(pass_context=True)
async def status(ctx):
    channel = ctx.channel
    member = ctx.message.author
    mod_ck = moderator_check(member)
    if (mod_ck is True) or member.guild_permissions.administrator:
        duration = int(time.time()) - systemstart
        dhours = (duration / 3600)
        emb = (discord.Embed(title="StormBot Status:", color=0xdc8545))
        emb.add_field(name='Uptime: ', value=(str(round(dhours, 2)) + "hrs"), inline=True)
        await channel.send(embed=emb)


@client.command(pass_context=True)
async def test(ctx):
    member = ctx.message.author
    if member.guild_permissions.administrator:
        launch_instance('StormBot-Instance-test.py', TOKEN, APIKEY)

'''
@client.command(pass_context=True)
async def change_nick(ctx):
    print('y')
    channel = ctx.channel
    message = ctx.message
    content = message.content.split()
    member = ctx.message.author
    print(str(content))
    if len(content) != 2:
        print('exit')
        await channel.send('The argument entered is incorrect \n'
                           'Try \'?change_nick BattleTag\'')
        return
    print('begin')
    await member.edit(nick='test')
    print('test')
    await channel.send('<@' + str(message.id) + '> Your Nickname has been updated to \'' + content[1] + '\'')
'''

@client.command(pass_context=True)
async def announcement(ctx):
    broadcast_list = [384886471531692033, 162706186272112640]
    #broadcast_list = [472466501883002891, 498694144403701760]#Test Server
    channel = ctx.channel
    message = ctx.message
    content = message.content.split()
    contentall = message.content
    member = ctx.message.author
    if moderator_check(member) or member.guild_permissions.administrator:
        if len(content) < 3:
            await channel.send('A tilte and message is required to have an announcement.'
                               ' Try \'?announcement Title Message\'')
            return
        remove = (len(content[0]) + len(content[1]) + 2)
        broadcast = contentall[remove:]
        temp = 0
        embed = discord.Embed(title=(content[1] + '    (PREVIEW)'),
                              description=broadcast, color=0x39b8e8)
        embed.set_footer(text='CoCo Clan Team   (' + str(member.id) + ')')
        await channel.send(embed=embed)
        await channel.send('This is a preview of the announcement.'
                           ' Type \'send\' to proceed or type \'cancel\' to discard. You have 40 seconds to respond!')

        def check(m):
            if m.content == 'send' and m.channel == channel:
                return m.content == 'send' and m.channel == channel
            if m.content == 'cancel' and m.channel == channel:
                return m.content == 'cancel' and m.channel == channel

        try:
            msg = await client.wait_for('message', check=check, timeout=40)
            if msg.content == 'cancel':
                await channel.send('<@' + str(member.id) + '> Message discarded')
            else:
                await channel.send('<@' + str(member.id) + '> Message sent')
                emb = discord.Embed(title=(content[1]),
                                      description=broadcast, color=0x39b8e8)
                emb.set_footer(text='CoCo Clan Team   (' + str(member.id) + ')')
                while temp < len(broadcast_list):
                    announce = client.get_channel(broadcast_list[temp])
                    await announce.send(embed=emb)
                    temp = temp + 1
        except asyncio.TimeoutError:
            await channel.send('<@' + str(member.id) + '> Command Timeout. Message Discarded')


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


def check_clan(member):
    roles = fetch_roles(member)
    clan_found = False
    for i in range(20):  # i'm projecting here
        if ('Clan ' + str(i)) in roles:
            clan_found = True
            clan_num = i
            break
    if not clan_found:
        clan_num = 0  # default 'error' value
    return clan_num


@client.command(pass_context=True)
async def staff(ctx):
    channel = ctx.channel
    author = ctx.message.author
    server = ctx.guild

    clan_num = check_clan(author)
    clan_string = 'Clan ' + str(clan_num)

    headmod_found = False
    mod_found = False
    lead_found = False

    hmods = []
    mods = []
    for member in server.members:
        roles = fetch_roles(member)
        roles_list = member.roles  # to allow for equating directly, otherwise moderator and head mods get mixed
        if clan_string in roles:
            for role in roles_list:
                if 'Head Moderator' == role.name:
                    headmod_found = True
                    hmods.append(member.mention)
                if 'Moderator' == role.name:
                    mod_found = True
                    mods.append(member.mention)
                if 'Leader' == role.name:
                    lead_found = True
                    lead = member.mention

    if not headmod_found:
        hmods = 'NIL'
    if not mod_found:
        mods = 'NIL'
    if not lead_found:
        lead = 'NIL'

    emb = (discord.Embed(title="Collective Conscious " + clan_string + " Staff",
                         description="These are your " + clan_string + " staff. Head Moderators and Admins can help with"
                                                                       " joining the clan. Moderators can help with any other inquiries.",
                         color=0x49ad3f))
    emb.add_field(name='Leader', value=lead, inline=True)
    emb.add_field(name='Head Moderator', value=', '.join(hmods), inline=True)
    emb.add_field(name='Moderator', value=', '.join(mods), inline=True)
    await channel.send(embed=emb)


client.loop.create_task(list_servers())
client.loop.create_task(display())
client.loop.create_task(msg_broadcast(client))
client.run(TOKEN, bot=True, reconnect=True)
