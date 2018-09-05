import discord
import pyodbc
from odbc.mssql import *
import time


# CONFIG
'''
config_file = open("StormBot.config", "r")
storm_config = config_file.readlines()
config_file.close()
server_id = '162706186272112640'  # StormBot

server = str(storm_config[0]).strip()
database = str(storm_config[1]).strip()
username = str(storm_config[2]).strip()
_password = str(storm_config[3]).strip()


async def update_coco_roles(sql, client, clan_id, clan_name):
    # HANDLE ROLES CHANGES AND LOW ACTIVITY
    discord_server = client.get_server(server_id)
    cur = mssql.select(sql, "select distinct r.MembershipId, r.[User_ID] from StageDiscordRoleChange r join "
                                 "ClanMembers m on m.MembershipId=r.MembershipId where Commited = 0 and m.ClanId=?"
                            , clan_id)
    rows = cur.fetchall()
    low_activity_count = 0
    kicked_count = 0
    frequenter_count = 0
    veteran_count = 0
    respected_count = 0
    do_not_remove = ['Founder', 'Clan Leader', 'Admin', 'Ascended Processors', 'Hidden Admin']
    for row in rows:
        membership_id = row.MembershipId
        discord_id = row.User_ID
        discord_member = discord_server.get_member(discord_id)
        print("Updating Membership: " + str(membership_id) + ", Discord Member: " + str(discord_member))

        # REMOVE ALL ROLES FROM MEMBER
        current_roles = fetch_roles(discord_member)
        for role in current_roles:
            if role in do_not_remove:
                await client.say("Cannot remove role " + str(role) + " from " + str(discord_member))
                continue
            else:
                await remove_roles(client, role, discord_member)
                print("Removed " + str(role) + " from " + str(discord_member))

        # ADD NEW ROLES TO MEMBER
        cur2 = mssql.select(sql, "select * from StageDiscordRoleChange r where MembershipId=? and Commited=0"
                            , membership_id)
        rows2 = cur2.fetchall()
        for new_roles in rows2:
            role_name = new_roles.RoleName
            r = discord.utils.get(discord_server.roles, name=role_name)
            await client.add_roles(discord_member, r)
            print("Added role " + str(r) + " to Member " + str(discord_member))
            if role_name == 'Low Activity':
                low_activity_count += 1
                await low_activity(client, discord_member)
            if role_name == 'Frequenter':
                frequenter_count += 1
            if role_name == 'Veteran':
                veteran_count += 1
            if role_name == 'Respected':
                respected_count += 1
            mssql.update(sql, "update r set Commited=1 from StageDiscordRoleChange r where RoleName = ? "
                              "and MembershipId=?", role_name, membership_id)

    # HANDLE KICKED MEMBERS
    cur3 = mssql.select(sql, "select r.*,m.DiscordID from StageRemoveClanMember r join ClanMembers m on "
                             "m.MembershipId=r.MembershipId where Commited=0 and ClanId=?", clan_id)
    kicked_rows = cur3.fetchall()
    for kicked in kicked_rows:
        kicked_count += 1
        discord_id = kicked.DiscordID
        membership_id = kicked.MembershipId
        discord_member = discord_server.get_member(discord_id)
        print("Kicking Membership: " + str(membership_id) + ", Discord Member: " + str(discord_member))

        # REMOVE ALL ROLES FROM MEMBER
        current_roles = fetch_roles(discord_member)
        for role in current_roles:
            if role in do_not_remove:
                await client.say("Cannot remove role " + str(role))
                continue
            else:
                await remove_roles(client, role, discord_member)
                print("Removed " + str(role) + " from " + str(discord_member))

        # ADD GUEST ROLE TO USER
        r = discord.utils.get(discord_server.roles, name="Guest")
        await client.add_roles(discord_member, r)

        mssql.update(sql, "update StageRemoveClanMember set Commited=1 where MembershipId=?", membership_id)

    embed = purge_results(clan_name, low_activity_count, kicked_count, frequenter_count, veteran_count, respected_count)
    await client.say(embed=embed)


async def remove_roles(client, role, clan_member):
    discord_server = client.get_server(server_id)
    role_to_remove = discord.utils.get(discord_server.roles, name=role)
    await client.remove_roles(clan_member, role_to_remove)


def purge_results(clan, low_activity_count, kicked_count, frequenter_count, veteran_count, respected_count):
    embed = discord.Embed(title=str(clan) + " Purge Results:")
    embed.add_field(name="Total Low Activity Members", value=str(low_activity_count), inline=False)
    embed.add_field(name="Total Kicked Members", value=str(kicked_count), inline=False)
    embed.add_field(name="Total Frequenter Promotions", value=str(frequenter_count), inline=False)
    embed.add_field(name="Total Veteran Promotions", value=str(veteran_count), inline=False)
    embed.add_field(name="Total Respected Promotions", value=str(respected_count), inline=False)
    return embed


async def low_activity(client, member):
    embed = discord.Embed(title="You have been made low activity",
                          description="What does this mean and what can you do?", color=0x008000)
    embed.add_field(name='1. Clan Activity',
                    value="The Collective Conscious staff takes its clan members' activity very seriously. Our goal "
                          "is to be the most active PC clan community in Destiny 2. We only have so many slots in each "
                          "clan, and these slots are constantly filling as new players find us and join. ",
                    inline=False)
    embed.add_field(name='2. Discord Activity', value="Maintaining consistent Discord activity means that you are "
                                                      "engaging with your fellow clan members in the community. While "
                                                      "we don't expect you to always be on and chatting with other "
                                                      "members, we do expect that you are using the Requests "
                                                      "channel to find games to play, and using the provided Voice "
                                                      "Channels to communicate with others. As such, your Destiny game "
                                                      "play coincides with your Discord activity. This means that "
                                                      "we judge your Destiny game play activity with how often you are "
                                                      "playing with clan members in the server.",
                    inline=False)
    embed.add_field(name='3. Where do you go from here?', value="Low Activity indicates unsatisfactory activity within "
                                                                "Destiny 2 and with fellow clan members. Increase your "
                                                                "activity by playing strikes, nightfalls, raids, "
                                                                "Crucible, etc. with clan members and the role will be "
                                                                "removed the next time your clan staff perform a clan "
                                                                "activity check.",
                    inline=False)
    embed.add_field(name="4. What happens if your activity doesn't improve?", value="After one week of being marked as "
                                                                                    "Low Activity, if your activity "
                                                                                    "both in Game, as well as the "
                                                                                    "Discord server, you will be "
                                                                                    "kicked from your respective clan. "
                                                                                    "After this kick, you will have "
                                                                                    "ONE second chance to rejoin any "
                                                                                    "Collective Conscious clan. If this "
                                                                                    "is your second time being made "
                                                                                    "Low Activity, if your activity "
                                                                                    "doesn't improve, you will be "
                                                                                    "banned from becoming a Collective "
                                                                                    "Consious clan member.",
                    inline=False)
    embed.set_footer(text='I\'m a bot. If you have questions, please contact a Clan Leader, Admin, or Moderator!')
    await client.send_message(member, embed=embed)


def fetch_roles(member):
    try:
        roles_list_ob = member.roles
        roles_len = len(roles_list_ob)
        if roles_len != 0:
            temp4 = 1
            roles_st = []
            while temp4 < roles_len:
                roles_st.append(roles_list_ob[temp4].name)
                # if temp4 >= 1:
                    # roles_st = roles_st + ','
                temp4 += 1
            return roles_st
        else:
            return 'NONE'
    except Exception as e:
        print(e)'''


