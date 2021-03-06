import traceback
import logging
import re
from discord.ext.commands import Bot, MemberConverter
from monitor.MemberMonitor import *
from monitor.MessageBroadcast import *
from monitor.Guild import *
from instance.main import *
from datetime import datetime, timedelta
systemstart = int(time.time())

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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
key = str(BOT_CONFIG[1]).strip()
api_url = str(BOT_CONFIG[2]).strip()
server_startime = time.time()

BOT_PREFIX = "?"
client = Bot(command_prefix=BOT_PREFIX)


@client.event
async def on_voice_state_update(member, before, after):
    await voip_tracker(member, before, after)


@client.event
async def on_message(message):
    await message_tracker(client, message)
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

'''
@client.event
async def on_message_delete(message):
    await delete_message(client, message)


@client.event
async def on_message_edit(before, after):
    await edit_message(client, before, after)
'''


@client.event
async def on_guild_join(guild):
    await join_guild(client, guild)


@client.event
async def on_guild_remove(guild):
    await leave_guild(client, guild)


@client.event
async def on_guild_update(before, after):
    await update_guild(client, before, after)


@client.event
async def on_guild_role_create(role):
    await add_guild_role(client, role)


@client.event
async def on_guild_role_delete(role):
    await remove_guild_role(client, role)


@client.event
async def on_guild_role_update(before, after):
    await update_guild_role(client, before, after)


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
            await client.change_presence(activity=discord.Game(str(BOT_PREFIX) + "help | V3.4.2"))
            #await client.change_presence(activity=discord.Game("TEST IN PROGRESS"))
            await asyncio.sleep(600)
            #await client.change_presence(activity=discord.Game("V2.0"))
            #await asyncio.sleep(20)
    except Exception as e:
        log_exception(str(e))

'''
@client.command(pass_context=True)
async def fupdate_server_roles(ctx):
    channel = ctx.channel
    message = ctx.message
    member = ctx.message.author
    
    for roles in member.guild.roles:
'''


@client.command(pass_context=True, description="Gets the Members activity of current week."
                                               " 'Use ?activty' for your user or '?acticty @Member'"
                                               " for another user")
async def activity(ctx):
    channel = ctx.channel
    message = ctx.message
    content = message.content
    member = ctx.message.author
    mod_ck = moderator_check(member)
    if "<@" in content:
        member_id = str(content[12:-1])
        temp_con = str(content[12:-1])
        if "!" in member_id:
            member_id = temp_con[1:]
    if str(content[10:-1]).isnumeric():
        print(str(content[10:]))
        member_id = str(content[10:])
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

    if temp == temp2:
        sevenday = datetime.timedelta(days=7)
        lastSunday -= sevenday
        temp = str(lastSunday).split('-')

    begin = datetime.datetime.now().replace(day=int(temp[2]), year=int(temp[0]), month=int(temp[1]))
    end = datetime.datetime.now().replace(day=int(temp2[2]), year=int(temp2[0]), month=int(temp2[1]))

    reg = str(requests.get(api_url + "/API/GetMember.php?id=" + str(key) + "&DiscordID=" + str(member.id)
                           + "&ServerID=" + str(member.guild.id) + "", verify=False).content)[3:-2]
    user = reg.split(";")
    if user[1] == '':
        emb = (discord.Embed(title="Activity Request:",
                             color=0x49ad3f))
        emb.add_field(name='Error - Bad Request', value=('No member matching id *' + str(member_id) + '* was found in the database'), inline=True)
        emb.set_footer(text='Requested By: (' + str(member.id) + ') ' + str(member))
    else:
        reg2 = str(requests.get(api_url + "/API/GetActivity.php?id=" + str(key) + "&DiscordID=" + str(member.id)
                               + "&ServerID=" + str(member.guild.id) + "&StartDate=" + str(begin) + "&EndDate=" + str(end) + "", verify=False).content)[3:-2]
        activity = reg2.split(";")

        time = float(int(activity[0]) * 60)
        day = time // (24 * 3600)
        time = time % (24 * 3600)
        hour = time // 3600
        time %= 3600
        minutes = time // 60

        emb = (discord.Embed(title="Activity Request:",
                             description=("Date: " + "{:%Y-%m-%d}".format(begin) + " to " + "{:%Y-%m-%d}".format(end)),
                             color=0x49ad3f))
        emb.add_field(name='User', value=user[1], inline=True)
        emb.add_field(name='User ID', value=user[2], inline=True)
        emb.add_field(name='Nickname/BattleTag', value=user[3], inline=True)
        emb.add_field(name='Discord Voice Time', value=("%dd %dh %dm" % (day, hour, minutes)), inline=True)
        emb.add_field(name='Discord Messages Sent', value=activity[1], inline=True)
        emb.set_footer(text='Requested By: (' + str(member.id) + ') ' + str(member))
    await channel.send(embed=emb)


@client.command(pass_context=True)
async def status(ctx):
    channel = ctx.channel
    member = ctx.message.author
    mod_ck = moderator_check(member)
    if (mod_ck is True) or member.guild_permissions.administrator:
        dbs = requests.get(api_url + "/API/DBStatus.php?id=" + str(key) + "", verify=False).content
        duration = float(time.time()) - systemstart
        day = duration // (24 * 3600)
        duration = duration % (24 * 3600)
        hour = duration // 3600
        duration %= 3600
        minutes = duration // 60
        duration %= 60
        seconds = duration
        emb = (discord.Embed(title="StormBot Status:", color=0xdc8545))
        emb.add_field(name='Uptime: ', value=("%dd %dh %dm %ds" % (day, hour, minutes, seconds)), inline=False)
        emb.add_field(name='Latency: ', value=(str(round(client.latency, 2)) + "s"), inline=False)
        emb.add_field(name='Database: ', value=(str(dbs)[2:-1]), inline=False)
        await channel.send(embed=emb)

'''
@client.command(pass_context=True)
async def admin_portal(ctx):
    channel = ctx.channel
    member = ctx.message.author
    if admin_check(member):
        if member.guild.id == 162706186272112640 or member.id == 162705828883726336:
            get_auth = mssql.select(_sql, "SELECT * FROM WebAuth")
            auth = get_auth.fetchall()

            embed = discord.Embed(title="StormBot Web Auth", url=(url + '/Login.php?User=' + auth[0][0] + '&Pass=' + auth[0][1]), color=0x008000)
            embed.add_field(name='Server ID:',
                            value=auth[0][0],
                            inline=False)
            embed.add_field(name='Password:',
                            value=auth[0][1],
                            inline=False)
            embed.add_field(name='Website:',
                            value=url, inline=False)
            embed.set_footer(text='I\'m a bot. If you have questions, please contact ZombieEar')
            await member.send(embed=embed)

            embed2 = discord.Embed(title="StormBot Web Auth",
            description=('<@' + str(member.id) + '> I sent you a message containing the authentication information')
                                  , color=0x008000)
            embed2.set_footer(text='I\'m a bot. If you have questions, please contact ZombieEar')
            await channel.send(embed=embed2)
'''

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


def admin_check(member):#check if user is in a Moderator
    try:
        result = False
        officer = 'Officer'
        head_sherpa = 'Head Sherpa'

        roles = fetch_roles(member)

        if member.guild_permissions.administrator:
            result = True
        if officer in roles:
            result = True
        if head_sherpa in roles:
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

    week_re = re.compile('\d*\.?\d+ Week')
    month_re = re.compile('\d*\.?\d+ Month')
    year_re = re.compile('\d*\.?\d+ Year')

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
            week_roles_values.append(float(re.search(week_re, role_str).group().split()[0]))
        elif re.search(month_re, role_str) is not None:
            month_roles.append(server_roles[i])
            month_roles_values.append(float(re.search(month_re, role_str).group().split()[0]))
        elif re.search(year_re, role_str) is not None:
            year_roles.append(server_roles[i])
            year_roles_values.append(float(re.search(year_re, role_str).group().split()[0]))

    print(', '.join([str(i) for i in week_roles]))
    print(', '.join([str(i) for i in month_roles]))
    print(', '.join([str(i) for i in year_roles]))

    # we arrange them backwards because we want to start searching for the longest time first later
    arrangedWeekRoles = [week_roles[i] for i in sorted(range(len(week_roles_values)), key=lambda k: week_roles_values[k]
                                                       , reverse=True)]
    arrangedWeek_timedeltas = [timedelta(days=7*week_roles_values[i]) for i in
                               sorted(range(len(week_roles_values)), key=lambda k: week_roles_values[k], reverse=True)]

    arrangedMonthRoles = [month_roles[i] for i in sorted(range(len(month_roles_values)), key=lambda k:month_roles_values[k]
                                                       , reverse=True)]
    arrangedMonth_timedeltas = [timedelta(days=30 * month_roles_values[i]) for i in
                                sorted(range(len(month_roles_values)), key=lambda k: month_roles_values[k], reverse=True)]

    arrangedYearRoles = [year_roles[i] for i in sorted(range(len(year_roles_values)), key=lambda k:year_roles_values[k]
                                                       , reverse=True)]
    arrangedYear_timedeltas = [timedelta(days=365 * year_roles_values[i]) for i in
                               sorted(range(len(year_roles_values)), key=lambda k: year_roles_values[k], reverse=True)]


    # we assume that all year trophies > month trophies > week trophies etc. e.g. there are no '5 Week' trophies
    arrangedRoles = [role for sublist in [arrangedYearRoles,arrangedMonthRoles,arrangedWeekRoles] for role in sublist]
    arrangedRoles_timedeltas = [td for sublist in
                                [arrangedYear_timedeltas,arrangedMonth_timedeltas,arrangedWeek_timedeltas]
                                for td in sublist]

    print(', '.join([str(i) for i in arrangedRoles]))
    print(', '.join([str(i.days) for i in arrangedRoles_timedeltas]))

    return arrangedRoles, arrangedRoles_timedeltas


# this is the hidden function, not the command
async def updateTimeRoles_function(timenow, member, rolesTrophies_ID, rolesTrophies_tds, updatedMembers, updatedTrophies_ID):
    roles = member.roles  # to allow for equating directly, otherwise moderator and head mods get mixed
    join_date = member.joined_at

    member_age = timenow - join_date
    print('Member '+str(member.display_name)+' age is '+str(member_age.days)+' days')

    for i in range(len(rolesTrophies_ID)):
        # iterate down the pre-arranged list in descending order

        if member_age >= rolesTrophies_tds[i]:
            roleGiven = rolesTrophies_ID[i]  # place this outside the conditionals..

            if roleGiven not in roles:  # then you give him the role
                print('attempting to update ' + str(rolesTrophies_ID[i]) + ' trophy for ' + str(member.display_name))
                updatedMembers.append(member.mention)
                updatedTrophies_ID.append(rolesTrophies_ID[i])

                await member.add_roles(rolesTrophies_ID[i])
            else:
                print(str(member.display_name)+' already has the correct trophy!')

            # after you've given him the role (or he already has it), iterate over everything else to remove the rest
            for old_role in rolesTrophies_ID:
                if old_role in roles and old_role is not roleGiven:
                    print('attempting to remove previous role ' + str(old_role) + ' for ' + str(member.display_name))
                    await member.remove_roles(old_role)
            break  # you break on the largest trophy, but only update if it's not currently the right one

    return updatedMembers, updatedTrophies_ID


@client.command(pass_context=True)
async def updateIndivTimeRoles(ctx, arg):
    channel = ctx.channel
    server = ctx.guild
    rolesTrophies_ID, rolesTrophies_tds = getServerTimeRoles(server)
    timenow = datetime.now()

    mc = MemberConverter()
    member = await mc.convert(ctx, arg)
    print('Trying to update this user: ' + str(member.display_name))

    updatedMembers, updatedTrophies_ID = await updateTimeRoles_function(timenow, member,
                                                                        rolesTrophies_ID, rolesTrophies_tds, [], [])
    if (len(updatedTrophies_ID)>0):
        emb = (discord.Embed(title="Membership Trophy Role Update",
                             description=member.mention+" has had their trophies updated:",
                             color=0x49ad3f))
        emb.add_field(name='New Trophy', value=(updatedTrophies_ID[0]),  # there should only be one anyway..
                      inline=False)
    else:
        emb = (discord.Embed(title="Membership Trophy Role Update",
                             description=member.mention+" already has the correct trophy!"
                                                        " Any erroneous trophies should have been removed..",
                             color=0x49ad3f))
    await channel.send(embed=emb)


@client.command(pass_context=True)
async def updateTimeRoles(ctx):
    channel = ctx.channel
    server = ctx.guild

    rolesTrophies_ID, rolesTrophies_tds = getServerTimeRoles(server)

    timenow = datetime.now()

    updatedMembers = []
    updatedTrophies_ID = []

    for member in server.members:
        updatedMembers, updatedTrophies_ID = await updateTimeRoles_function(timenow, member, rolesTrophies_ID,
                                                                      rolesTrophies_tds, updatedMembers,
                                                                      updatedTrophies_ID)

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
#client.loop.create_task(update_password(client))
client.loop.create_task(msg_broadcast(client))
client.run(TOKEN, bot=True, reconnect=True)
