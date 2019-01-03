import sys
import traceback
import logging
import re
from discord.ext.commands import Bot
from monitor.MemberMonitor import *
from monitor.MessageBroadcast import *
from instance.main import *
from db import *
from datetime import datetime, timedelta
systemstart = int(time.time())

_sql = mssql()


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
            await client.change_presence(activity=discord.Game(str(BOT_PREFIX) + "help | V3.0.1"))
            #await client.change_presence(activity=discord.Game("TEST IN PROGRESS"))
            #await asyncio.sleep(20)
            #await client.change_presence(activity=discord.Game("V2.0"))
            #await asyncio.sleep(20)
    except Exception as e:
        log_exception(str(e))


@client.command(pass_context=True)
async def activity(ctx):
    channel = ctx.channel
    message = ctx.message
    content = message.content
    member = ctx.message.author
    mod_ck = moderator_check(member)
    if not((mod_ck is True) or member.guild_permissions.administrator):
        return
    if "<@" in content:
        member_id = str(content[12:-1])
        temp_con = str(content[12:-1])
        if "!" in member_id:
            member_id = temp_con[1:]
    else:
        member_id = str(member.id)

    import datetime, calendar

    lastSunday = datetime.date.today()
    nextSunday = datetime.date.today()

    oneday = datetime.timedelta(days=1)

    while lastSunday.weekday() != calendar.SUNDAY:
        lastSunday -= oneday
    while nextSunday.weekday() != calendar.SUNDAY:
        nextSunday += oneday

    temp = str(lastSunday).split('-')
    temp2 = str(nextSunday).split('-')

    begin = datetime.datetime.now().replace(day=int(temp[2]), year=int(temp[0]), month=int(temp[1]))
    end = datetime.datetime.now().replace(day=int(temp2[2]), year=int(temp2[0]), month=int(temp2[1]))

    get_user = mssql.select(_sql, "SELECT * FROM DiscordUsers WHERE DiscordID = ? and ServerID = ?"
                            , str(member.id), member.guild.id)
    user = get_user.fetchall()

    get_activity = mssql.select(_sql, "SELECT SUM(Messages_Sent) AS MSG, SUM(Minutes_Voice) AS VOIP"
                                      " FROM DiscordActivity"
                                      " WHERE (DiscordID = ?) and (ServerID = ?)"
                                      " and ActivityDate between cast(? as datetime) and cast(? as datetime)"
                                , str(member.id), str(member.guild.id), begin, end)
    activity = get_activity.fetchall()

    time = float(int(activity[0][1]) * 60)
    day = time // (24 * 3600)
    time = time % (24 * 3600)
    hour = time // 3600
    time %= 3600
    minutes = time // 60

    emb = (discord.Embed(title="Activity Request:",
                         description=("Date: " + "{:%Y-%m-%d}".format(begin) + " to " + "{:%Y-%m-%d}".format(end)),
                         color=0x49ad3f))
    emb.add_field(name='User', value=user[0][1], inline=True)
    emb.add_field(name='User ID', value=user[0][2], inline=True)
    emb.add_field(name='Nickname/BattleTag', value=user[0][3], inline=True)
    emb.add_field(name='Discord Voice Time', value=("%dd %dh %dm" % (day, hour, minutes)), inline=True)
    emb.add_field(name='Discord Messages Sent', value=activity[0][0], inline=True)
    emb.set_footer(text='Requested By: (' + str(member.id) + ') ' + str(member))
    await channel.send(embed=emb)

'''
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
'''

@client.command(pass_context=True)
async def status(ctx):
    channel = ctx.channel
    member = ctx.message.author
    mod_ck = moderator_check(member)
    if (mod_ck is True) or member.guild_permissions.administrator:
        duration = float(time.time()) - systemstart
        day = duration // (24 * 3600)
        duration = duration % (24 * 3600)
        hour = duration // 3600
        duration %= 3600
        minutes = duration // 60
        duration %= 60
        seconds = duration
        emb = (discord.Embed(title="StormBot Status:", color=0xdc8545))
        emb.add_field(name='Uptime: ', value=("%dd %dh %dm %ds" % (day, hour, minutes, seconds)), inline=True)
        await channel.send(embed=emb)


@client.command(pass_context=True)
async def test(ctx):
    member = ctx.message.author
    if member.guild_permissions.administrator:
        mssql.select(_sql, "INSERT INTO DiscordUsers VALUES (?, ?, ?, ?, ?)"
                     , "ZombieEar#0493", "162705828883726336", "None", 451097751975886858, 0)

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
    admin_found = False

    hmods = []
    mods = []
    lead = ''
    admin = ''
    for member in server.members:
        roles = fetch_roles(member)
        roles_list = member.roles  # to allow for equating directly, otherwise moderator and head mods get mixed
        if clan_string in roles:
            for role in roles_list:
                if 'Clan Leader' == role.name:
                    lead_found = True
                    lead = member.mention
                if 'Admin' == role.name:
                    do_not_include = False
                    for member_role in member.roles:
                        if member_role.name == 'Clan Leader':
                            do_not_include = True
                    if do_not_include is False:
                        admin_found = True
                        admin = member.mention
                if 'Head Moderator' == role.name:
                    do_not_include = False
                    for member_role in member.roles:
                        if member_role.name == 'Clan Leader' or member_role.name == 'Admin':
                            do_not_include = True
                    if do_not_include is False:
                        headmod_found = True
                        hmods.append(member.mention)
                if 'Moderator' == role.name:
                    do_not_include = False
                    for member_role in member.roles:
                        if member_role.name == 'Head Moderator' or member_role.name == 'Admin':
                            do_not_include = True
                    if do_not_include is False:
                        mod_found = True
                        mods.append(member.mention)

    if not headmod_found:
        hmods = 'None'
    if not mod_found:
        mods = 'None'
    if not lead_found:
        lead = 'None'
    if not admin_found:
        admin = 'None'

    # print(str(headmod_found) + ', ' +  str(mod_found) + ', ' + str(lead_found) + ', ' + str(admin_found))
    # print(str(hmods) + ', ' + str(mods) + ', ' + str(lead) + ', ' + str(admin))
    print('Sending ?staff command to ' + str(ctx.channel))

    emb = (discord.Embed(title="Collective Conscious " + clan_string + " Staff",
                         description="These are your " + clan_string + " staff. Head Moderators and Admins can help with"
                                                                       " joining the clan. Moderators can help with any other inquiries.",
                         color=0x49ad3f))
    emb.add_field(name='Clan Leader', value=lead, inline=True)
    emb.add_field(name='Admins', value=str(admin), inline=True)
    if headmod_found:
        emb.add_field(name='Head Moderator', value=', '.join(hmods), inline=True)
    else:
        emb.add_field(name='Head Moderator', value=hmods, inline=True)
    if mod_found:
        emb.add_field(name='Moderator', value=', '.join(mods), inline=True)
    else:
        emb.add_field(name='Moderator', value=mods, inline=True)
    await channel.send(embed=emb)


def getServerTimeRoles(server):
    server_roles = server.roles

    week_re = re.compile('\d+ Week')
    month_re = re.compile('\d+ Month')
    year_re = re.compile('\d+ Year')

    week_roles = []
    month_roles = []
    year_roles = []
    week_roles_values = []
    month_roles_values = []
    year_roles_values = []

    for i in range(len(server_roles)):
        role_str = str(server_roles[i])
        if re.search(week_re, role_str) is not None:
            week_roles.append(server_roles[i])
            week_roles_values.append(int(re.search(week_re, role_str).group().split()[0]))
        elif re.search(month_re, role_str) is not None:
            month_roles.append(server_roles[i])
            month_roles_values.append(int(re.search(month_re, role_str).group().split()[0]))
        elif re.search(year_re, role_str) is not None:
            year_roles.append(server_roles[i])
            year_roles_values.append(int(re.search(year_re, role_str).group().split()[0]))

    print(', '.join([str(i) for i in week_roles]))
    print(', '.join([str(i) for i in month_roles]))
    print(', '.join([str(i) for i in year_roles]))

    # we arrange them backwards because we want to start searching for the longest time first later
    arrangedWeekRoles = [week_roles[i] for i in sorted(range(len(week_roles_values)), key=lambda k: week_roles_values[k]
                                                       , reverse=True)]
    arrangedWeek_timedeltas = [datetime.timedelta(days=7*week_roles_values[i]) for i in
                               sorted(range(len(week_roles_values)), key=lambda k: week_roles_values[k], reverse=True)]

    arrangedMonthRoles = [month_roles[i] for i in sorted(range(len(month_roles_values)), key=lambda k:month_roles_values[k]
                                                       , reverse=True)]
    arrangedMonth_timedeltas = [datetime.timedelta(days=30 * month_roles_values[i]) for i in
                                sorted(range(len(month_roles_values)), key=lambda k: month_roles_values[k], reverse=True)]

    arrangedYearRoles = [year_roles[i] for i in sorted(range(len(year_roles_values)), key=lambda k:year_roles_values[k]
                                                       , reverse=True)]
    arrangedYear_timedeltas = [datetime.timedelta(days=365 * year_roles_values[i]) for i in
                               sorted(range(len(year_roles_values)), key=lambda k: year_roles_values[k], reverse=True)]


    # we assume that all year trophies > month trophies > week trophies etc. e.g. there are no '5 Week' trophies
    arrangedRoles = [role for sublist in [arrangedYearRoles,arrangedMonthRoles,arrangedWeekRoles] for role in sublist]
    arrangedRoles_timedeltas = [td for sublist in
                                [arrangedYear_timedeltas,arrangedMonth_timedeltas,arrangedWeek_timedeltas]
                                for td in sublist]

    print(', '.join([str(i) for i in arrangedRoles]))
    print(', '.join([str(i) for i in arrangedRoles_timedeltas]))

    return arrangedRoles, arrangedRoles_timedeltas

	
@client.command(pass_context=True)
async def updateTimeRoles(ctx):
    channel = ctx.channel
    server = ctx.guild

    rolesTrophies_ID, rolesTrophies_tds = getServerTimeRoles(server)

    # monthTrophies = [5, 3, 2, 1]
    # roleTrophies = [(str(i) + ' Month') for i in monthTrophies]

    # rolesTrophies_ID = [discord.utils.get(server.roles, name=i) for i in roleTrophies]

    timenow = datetime.datetime.now()

    updatedMembers = []
    updatedTrophies_ID = []

    for member in server.members:
        # roles = fetch_roles(member)
        roles = member.roles  # to allow for equating directly, otherwise moderator and head mods get mixed
        join_date = member.joined_at
        # monthsAge = int((timenow-join_date).days/30)

        # print(member.display_name + " joined at " + str(join_date) + ", months elapsed since then = " + str(monthsAge))

        member_age = timenow - join_date

        for i in range(len(rolesTrophies_ID)):
            # iterate down the pre-arranged list in descending order

            if member_age >= rolesTrophies_tds[i]:
                if rolesTrophies_ID[i] not in roles:
                    print('attempting to update ' + str(rolesTrophies_ID[i]) + ' trophy for ' + str(member.display_name))
                    updatedMembers.append(member.mention)
                    updatedTrophies_ID.append(rolesTrophies_ID[i])
                    await member.add_roles(rolesTrophies_ID[i])

                    # only need to iterate over smaller ages
                    for old_role in rolesTrophies_ID[i+1:]:
                        if old_role in roles:
                            print('attempting to remove previous role ' + str(old_role) + ' for ' + str(member.display_name))
                            await member.remove_roles(old_role)
                break  # you break on the largest monthTrophy, but only update if it's not currently the right one

    emb = (discord.Embed(title="Membership Trophy Role Updates",
                         description="The following members have had their trophies updated:",
                         color=0x49ad3f))
    for i in range(len(rolesTrophies_ID)):
        clippedMembers = []
        for k in range(len(updatedMembers)):  # form the shortened list
            if updatedTrophies_ID[k] == rolesTrophies_ID[i]:
                clippedMembers.append(updatedMembers[k])
        if len(clippedMembers) > 0:
            emb.add_field(name='New ' + str(rolesTrophies_ID[i]) + ' Trophies', value=(','.join(clippedMembers)),
                          inline=False)
        else:
            emb.add_field(name='New ' + str(rolesTrophies_ID[i]) + ' Trophies', value='None',
                          inline=False)

    await channel.send(embed=emb)


client.loop.create_task(list_servers())
client.loop.create_task(display())
client.loop.create_task(msg_broadcast(client))
client.run(TOKEN, bot=True, reconnect=True)
