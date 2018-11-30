from init import g, client, BNET_APIKEY, TOKEN, LOCALE, CHANNEL_GUILD_ID, ILVL_LIMIT, REGION as APIREGION, ROLE_ALLOWED
import discord
import asyncio
import requests
import argparse
from models.character import Character

USAGE_MSG = 'Valid command: \n' \
            '!help: get bot usage \n' \
            '!register <server> <guildName>: Register a new guild for refresh data members\n' \
            '!unregister <server> <guildName>: Unregister a guild already register.\n' \
            '!ping: Test if the bot works.\n' \
            '!info: Get bot informations.\n' \
            '!leavers: Get players who left guilds and dont join a new guild.\n'

REGION = 1
SERVER = 2
GUILDNAME = 3
LEVEL_MAX = 120


def get_new_members(json):
    result = []
    for member in json['members']:
        member = member['character']
        try:
            Character.save_db(member['guild'], member['name'], member['realm'], member['level'])
            if int(member['level']) == 120:
                result.append(member['name'])
        except KeyError:
            continue
    return result


async def refresh_guilds():
    await client.wait_until_ready()
    while not client.is_closed:
        print("Refreshing guilds....")
        list = g['redis'].smembers('guilds')
        channel = discord.Object(id=CHANNEL_GUILD_ID)
        msg = ''
        for guild in list:
            url = 'https://{}.api.battle.net/wow/guild/{}/{}?fields=members&locale={}&apikey={}'.format(
                guild.split(':')[REGION],
                guild.split(':')[SERVER],
                guild.split(':')[GUILDNAME],
                LOCALE,
                BNET_APIKEY
            )
            old_members = g['redis'].smembers('{}:members'.format(guild))
            req = requests.get(url)
            if req.status_code != 200:
                continue
            new_members = get_new_members(req.json())
            name = req.json()['name']
            for member in old_members:
                if member not in new_members:
                    char = Character.from_db(name, member)
                    char = Character.refresh()
                    if char.ilvl > int(ILVL_LIMIT):
                        msg = msg + char.get_msg(True)
                    g['redis'].sadd('leavers', member)
                    g['redis'].srem('{}:members'.format(guild), member)
                    char.del_db()
            for member in new_members:
                if member not in old_members:
                    char = Character.from_db(name, member)
                    char.refresh()
                    if int(char.ilvl) > int(ILVL_LIMIT):
                        msg = msg + char.get_msg(False)
                        g['redis'].sadd('{}:members'.format(guild), member)
                    g['redis'].srem('leavers', member)

        print("Refreshing Done.")
        if msg != '':
            await client.send_message(channel, msg)
        await asyncio.sleep(300)


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!info'):
        msg = "Hello {}\n".format(message.author.mention)
        msg = msg + 'Region : {}\n' \
                    'Ilvl Limit : {}\n' \
                    'Channel : {}\n' \
                    'Guilds registered : '.format(APIREGION,
                                            ILVL_LIMIT,
                                            CHANNEL_GUILD_ID)
        for guild in g['redis'].smembers('guilds'):
            msg = msg + '{}, '.format(guild.split(':')[3].capitalize())
        await client.send_message(message.channel, msg)
        return
    allowed = False
    for role in message.author.roles:
        if ROLE_ALLOWED == role.id:
            allowed = True
    g['redis'].sadd('theobot:history', message.content)
    if message.author.id == "217354856980152320":
        allowed = True
    if message.content.startswith('!register'):
        if not allowed:
            await client.send_message(message.channel, "{} : You are not allowed to do this action."
                                      .format(message.author.mention))
            return
        args = message.content.capitalize().split(' ', 2)
        if len(args) < 3:
            await client.send_message(message.channel, 'Usage: !register <server> <guildName>')
        if register_guild(args[1], args[2]):
            await client.send_message(message.channel, "Guild registered.")
        else:
            await client.send_message(message.channel, "Guild not exist or already registered.")

    if message.content.startswith('!unregister'):
        if not allowed:
            await client.send_message(message.channel, "{} : You are not allowed to do this action."
                                      .format(message.author.mention))
            return
        args = message.content.capitalize().split(' ', 2)
        if len(args) < 3:
            await client.send_message(message.channel, 'Usage: !unregister <server> <guildName>')
        if register_guild(args[1], args[2]):
            await client.send_message(message.channel, "Guild unregistered.")
        else:
            await client.send_message(message.channel, "Guild not exist in database.")
    if message.content.startswith('!help'):
        await client.send_message(message.channel, USAGE_MSG)
    if message.content.startswith('!leavers'):
        leavers = g['redis'].smembers('leavers')
        if leavers:
            await client.send_message(message.channel, leavers)
        else:
            await client.send_message(message.channel, "No leavers at the moments")


def register_guild(server, guildname):
    if g['redis'].exists('guild:{}:{}:{}:members'.format(APIREGION, server, guildname)):
        g['redis'].sadd('guilds', 'guild:{}:{}:{}'.format(APIREGION, server, guildname))
        return True
    url = 'https://{}.api.battle.net/wow/guild/{}/{}?fields=members&locale={}&apikey={}'.format(
        APIREGION,
        server,
        guildname,
        LOCALE,
        BNET_APIKEY
    )
    rq = requests.get(url)
    if rq.status_code != 200:
        return False
    members = get_new_members(rq.json())
    g['redis'].sadd('guilds', 'guild:{}:{}:{}'.format(APIREGION, server, guildname))
    for member in members:
        char = Character.from_db(guildname, member)
        if int(char.level) == LEVEL_MAX:
            g['redis'].sadd('guild:{}:{}:{}:members'.format(APIREGION, server, guildname), member)
    return True


def unregister_guild(server, guildname):
    return g['redis'].srem('guilds', 'guild:{}:{}:{}'.format(APIREGION, server, guildname))


@client.event
async def on_ready():
    print("Logged in as")
    print(client.user.name)
    print(client.user.id)
    print('--------')


def launch():
    client.loop.create_task(refresh_guilds())
    client.run(TOKEN)


launch()
