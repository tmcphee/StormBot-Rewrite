import datetime
import requests

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

text_file = open("StormBot.config", "r")
BOT_CONFIG = text_file.readlines()
text_file.close()
key = str(BOT_CONFIG[1]).strip()
api_url = str(BOT_CONFIG[2]).strip()


#TESTED -- WORKING
async def join_guild(client, guild):
    send_url = api_url + "/API/Guild/AddGuild.php?id=" + str(key) + "&ServerID=" + \
               str(guild.id) + "&GuildName=" + str(guild.name) + "&OwnerID=" + str(guild.owner_id) + ""
    modified_url = send_url.replace(" ", "<>", 3)
    requests.get(modified_url, verify=False)
    print(str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M %p %Z")) + " -- [" + str(
        guild.id) + "] -> StormBot Joined A New Server")

    for role in guild.roles:
        send_url = api_url + "/API/Guild/AddRole.php?id=" + str(key) + "&RoleID=" + \
                  str(role.id) + "&RoleName=" + str(role.name) + "&Color=" + str(role.colour.value) + \
                  "&ServerID=" + str(role.guild.id) + "&IsAdmin=" + str(int(role.permissions.administrator)) + ""
        modified_url = send_url.replace(" ", "<>", 3)
        requests.get(modified_url, verify=False)

    print(str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M %p %Z")) + " -- [" + str(
        guild.id) + "] -> Finished syncing Roles to Database")


#TESTED -- WORKING
async def leave_guild(client, guild):
    send_url = api_url + "/API/Guild/RemoveGuild.php?id=" + str(key) + "&ServerID=" + \
               str(guild.id) + ""
    requests.get(send_url, verify=False)
    print(str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M %p %Z")) + " -- [" + str(
        guild.id) + "] -> StormBot Left A Server")


#TESTED -- WORKING
async def update_guild(client, before, after):
    if before.name != after.name:
        send_url = api_url + "/API/Guild/UpdateGuild.php?id=" + str(key) + "&ServerID=" + \
                   str(after.id) + "&GuildName=" + str(after.name) + "&OwnerID=" + str(after.owner_id) + ""
        modified_url = send_url.replace(" ", "<>", 3)
        requests.get(modified_url, verify=False)
        print(str(modified_url))
        print(str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M %p %Z")) + " -- [" + str(
            before.id) + "] -> Updated Server Name")

    if before.owner_id != after.owner_id:
        send_url = api_url + "/API/Guild/UpdateGuild.php?id=" + str(key) + "&ServerID=" + \
                   str(after.id) + "&GuildName=" + str(after.name) + "&OwnerID=" + str(
            after.owner_id) + ""
        modified_url = send_url.replace(" ", "<>", 3)
        requests.get(modified_url, verify=False)
        print(str(modified_url))
        print(str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M %p %Z")) + " -- [" + str(
            before.id) + "] -> Updated Server Owner")


#TESTED -- WORKING
async def update_guild_role(client, before, after):
    if before.name != after.name:
        send_url = api_url + "/API/Guild/UpdateRole.php?id=" + str(key) + "&RoleID=" + \
                   str(after.id) + "&RoleName=" + str(after.name) + "&Color=" + str(after.colour.value) + \
                   "&ServerID=" + str(after.guild.id) + "&IsAdmin=" + str(int(after.permissions.administrator)) + ""
        modified_url = send_url.replace(" ", "<>", 3)
        requests.get(modified_url, verify=False)
        print(str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M %p %Z")) + " -- [" + str(
            before.guild.id) + "] -> Updated Guild Role Name")

    if before.colour != after.colour:
        send_url = api_url + "/API/Guild/UpdateRole.php?id=" + str(key) + "&RoleID=" + \
                   str(after.id) + "&RoleName=" + str(after.name) + "&Color=" + str(after.colour.value) + \
                   "&ServerID=" + str(after.guild.id) + "&IsAdmin=" + str(int(after.permissions.administrator)) + ""
        modified_url = send_url.replace(" ", "<>", 3)
        requests.get(modified_url, verify=False)
        print(str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M %p %Z")) + " -- [" + str(
            before.guild.id) + "] -> Updated Guild Role Color")


async def add_guild_role(client,role):
    send_url = api_url + "/API/Guild/AddRole.php?id=" + str(key) + "&RoleID=" + \
               str(role.id) + "&RoleName=" + str(role.name) + "&Color=" + str(role.colour.value) + \
               "&ServerID=" + str(role.guild.id) + "&IsAdmin=" + str(int(role.permissions.administrator)) + ""
    modified_url = send_url.replace(" ", "<>", 3)
    requests.get(modified_url, verify=False)
    print(str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M %p %Z")) + " -- [" + str(
        role.guild.id) + "] -> Added Guild Role")


async def remove_guild_role(client, role):
    send_url = api_url + "/API/Guild/RemoveRole.php?id=" + str(key) + "&ServerID=" + \
               str(role.guild.id) + "&RoleID=" + str(role.id) + ""
    requests.get(send_url, verify=False)
    print(str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M %p %Z")) + " -- [" + str(
        role.guild.id) + "] -> Removed Guild Role")