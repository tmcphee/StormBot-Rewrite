import discord
from odbc.mssql import *


async def member_joined_discord(client, member):
    add_member_database(member)
    embed = discord.Embed(title="Welcome to Collective Conscious.",
                          description="CoCo is a PC-only Destiny 2 clan covering both NA and EU.", color=0x008000)
    embed.add_field(name='1. Server nickname',
                    value='Your nickname must match your BattleTag regardless of clan member status.\n'
                          'Example: PeachTree#11671\n Set your nickname using the command \'?change_nick BattleTag\'.',
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
    await client.send_message(member, embed=embed)
    print("-on_member_join      User Joined      User:" + str(member))


async def member_left_discord(client, member):
    print('')


async def update_member():
    print('')


def add_member_database(member):
    print("Warning 0012 -- MEMBER *" + str(member) + "* NOT FOUND - Adding user to DataBase")
    mssql.select("""INSERT INTO DiscordUsers VALUES (?, ?, ?, ?)""",
                (str(member), str(member.id), str(member.nick), str(member.guild.id)))