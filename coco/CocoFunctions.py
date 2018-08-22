import discord
import pyodbc
from odbc.mssql import *


# CONFIG
config_file = open("StormBot.config", "r")
storm_config = config_file.readlines()
config_file.close()
server_id = '162706186272112640'  # StormBot

server = str(storm_config[0]).strip()
database = str(storm_config[1]).strip()
username = str(storm_config[2]).strip()
_password = str(storm_config[3]).strip()
driver = str(storm_config[5]).strip()


async def update_coco_roles(sql, client, clan_id):
    low_activity_roles_remove = ['Clan 1 Member', 'Clan 2 Member', 'Clan 3 Member', 'Clan 4 Member', 'Clan 5 Member']
    discord_server = client.get_server(server_id)
    cur = mssql.select(sql, "select distinct r.MembershipId, User_ID from StageDiscordRoleChange r join "
                                 "ClanMembers m on m.MembershipId=r.MembershipId where Commited = 0 and m.ClanId=?"
                            , clan_id)
    low_activity_count = 0
    kicked_count = 0
    for row in cur:
        member_id = row[0]
        user_id = row[1]
        clan_member = discord_server.get_member(user_id)
        current_roles = fetch_roles(clan_member)
        cur2 = mssql.select(sql, "select d.* from StageDiscordRoleChange r join DiscordRoleDef d on "
                                      "d.RoleId=r.RoleId where r.MembershipId='" + str(member_id)
                                 + "' and Commited = 0")
        for role in cur2:
            role_name = role[1]
            try:
                r = discord.utils.get(discord_server.roles, name=role_name)
                await client.add_roles(clan_member, r)
                mssql.update(sql, "update r set Commited = 1 from StageDiscordRoleChange r join DiscordRoleDef d "
                                  "on d.RoleId=r.RoleId where r.MembershipId = '" + str(member_id)
                                  + "' and d.RoleName = '" + role_name + "'")
                if role_name == 'Low Activity':
                    low_activity_count += 1
                    try:
                        for role_cur in current_roles:
                            if role_cur in low_activity_roles_remove:

                                remove = discord.utils.get(discord_server.roles, name=role_cur)
                                await client.remove_roles(clan_member, remove)
                        await low_activity(client, clan_member)
                    except Exception as e:
                        print(e)
            except Exception as e:
                print(e)
    embed = purge_results(clan_id, low_activity_count, kicked_count)
    await client.say(embed=embed)


def purge_results(clan, low_activity_count, kicked_count):
    embed = discord.Embed(title=str(clan) + " purge results:")
    embed.add_field(name="Total Low Activity Members", value=str(low_activity_count))
    embed.add_field(name="Total Kicked Members", value=str(kicked_count))
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
            return roles_st[:-1]
        else:
            return 'NONE'
    except Exception as e:
        print(e)
