from autoredis import AutoRedis
import sys
import discord
import asyncio
import requests


USAGE_MSG = 'Valid command: \n' \
            '!help: get bot usage \n' \
            '!register <region> <server> <guildName>: Register a new guild for refresh data members\n' \
            '!unregister <region> <server> <guildName>: Unregister a guild already register.\n' \
            '!hello: Test if the bot works.\n'

g = dict()


TOKEN = 'NTE0ODc1MDE0NzU2MTcxNzc4.Dtc6eQ.wXWKicjAC3o_sZN76C7LLbQxKws'
BNET_APIKEY = '76t29cs8yr7jvfaqwyz7683vq7u6fsup'
LOCALE='fr_FR'

REGION = 1
SERVER = 2
GUILDNAME = 3

client = discord.Client()


try:
    g['redis'] = AutoRedis(('127.0.0.1', 6379),
                           password=None,
                           db=2,
                           decode_responses=True)
except (ConnectionError, KeyError):
    print('Error Database')
    sys.exit(-1)


def get_new_members(json):
    result = []
    for member in json['members']:
        result.append(member['character']['name'])
    return result


async def refresh_guilds():
    await client.wait_until_ready()
    while not client.is_closed:
        print("Refreshing guilds....")
        list = g['redis'].smembers('guilds')
        channel = discord.Object(id='516605516701630464')
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
            for member in old_members:
                if member not in new_members:
                    msg = msg + '{} left {}\n'.format(member, guild.split(':')[3])
                    g['redis'].sadd('leavers', member)
            g['redis'].delete('{}:members'.format(guild))
            for member in new_members:
                if member not in old_members:
                    msg = msg + '{} joined {}\n'.format(member, guild.split(':')[3])
                    g['redis'].srem('leavers', member)
                g['redis'].sadd('{}:members'.format(guild), member)

        print("Refreshing Done.")
        if msg != '':
            await client.send_message(channel, msg)
        await asyncio.sleep(300)


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    g['redis'].sadd('theobot:history', message.content)

    if message.content.startswith('!hello'):
        msg = "Hello {}".format(message.author.mention)
        await client.send_message(message.channel, msg)

    if message.content.startswith('!register'):
        args = message.content.upper().split(' ', 3)
        if len(args) != 4:
            await client.send_message(message.channel, 'Usage: !register <region> <server> <guildName>')
        if register_guild(args[1], args[2], args[3]):
            await client.send_message(message.channel, "Guild registered.")
        else:
            await client.send_message(message.channel, "Guild not exist or already registered.")

    if message.content.startswith('!unregister'):
        args = message.content.upper().split(' ', 3)
        if len(args) != 4:
            await client.send_message(message.channel, 'Usage: !unregister <region> <server> <guildName>')
        if register_guild(args[1], args[2], args[3]):
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


def register_guild(region, server, guildname):
    if g['redis'].exists('guild:{}:{}:{}:members'.format(region, server, guildname)):
        g['redis'].sadd('guilds', 'guild:{}:{}:{}'.format(region, server, guildname))
        return True
    url = 'https://{}.api.battle.net/wow/guild/{}/{}?fields=members&locale={}&apikey={}'.format(
        region,
        server,
        guildname,
        LOCALE,
        BNET_APIKEY
    )
    rq = requests.get(url)
    if rq.status_code != 200:
        return False
    members = get_new_members(rq.json())
    g['redis'].sadd('guilds', 'guild:{}:{}:{}'.format(region, server, guildname))
    for member in members:
        g['redis'].sadd('guild:{}:{}:{}:members'.format(region, server, guildname), member)
    return True


def unregister_guild(region, server, guildname):
    return g['redis'].srem('guilds', 'guild:{}:{}:{}'.format(region, server, guildname))


@client.event
async def on_ready():
    print("Logged in as")
    print(client.user.name)
    print(client.user.id)
    print('--------')


client.loop.create_task(refresh_guilds())
client.run(TOKEN)
