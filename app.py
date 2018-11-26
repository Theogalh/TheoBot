from autoredis import AutoRedis
from functools import wraps
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

client = discord.Client()


def database_open():
    try:
        g['redis'] = AutoRedis(('127.0.0.1', 6379),
                               password=None,
                               db=2,
                               decode_responses=True)
    except (ConnectionError, KeyError):
        return False

    return True


def database_required(func):
    @wraps(func)
    def decorated_func(*args, **kwargs):
        if database_open() is False:
            print("Can't connect to REDIS Server.")
            sys.exit(1)
        return func(*args, **kwargs)
    return decorated_func


def get_new_members(json):
    # TODO parser la requests pour avoir la liste des membres.
    return ['test', 'test2']


@database_required
async def refresh_guilds():
    await client.wait_until_ready()
    list = g['redis'].smembers('guilds')
    msg = str()
    for guild in list:
        old_members = g['redis'].smembers('{}:members'.format(guild))
        req = requests.get('')
        if req.status_code != 200:
            continue
        new_members = get_new_members(req.json())
        for member in old_members:
            if member not in new_members:
                msg = msg + '{} left {}\n'.format(member, guild.split(':')[3])
        g['redis'].delete('{}:members'.format(guild))
        for member in new_members:
            if member not in old_members:
                msg = msg + '{} join {}\n'.format(member, guild.split(':')[3])
            g['redis'].sadd('{}:members'.format(guild), member)

    channel = discord.Object(id='guild_infos')
    while not client.is_closed:
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
        msg = "Register works"
        args = message.content.split(' ')
        if len(args) != 4:
            await client.send_message(message.channel, 'Usage: !register <region> <server> <guildName>')
        if register_guild(args[1], args[2], args[3]):
            await client.send_message(message.channel, "Guild registered.")
        else:
            await client.send_message(message.channel, "Guild not exist.")

    if message.content.startswith('!unregister'):
        msg = "Register works"
        args = message.content.split(' ')
        if len(args) != 4:
            await client.send_message(message.channel, 'Usage: !unregister <region> <server> <guildName>')
        if register_guild(args[1], args[2], args[3]):
            await client.send_message(message.channel, "Guild unregistered.")
        else:
            await client.send_message(message.channel, "Guild not exist in database.")
    if message.content.startswith('!help'):
        await client.send_message(message.channel, USAGE_MSG)


@database_required
def register_guild(region, server, guildname):
    g['redis'].sadd('guilds', 'guild:{};{};{}'.format(region, server, guildname))
    g['redis'].sadd('guild:{};{};{}:members'.format(region, server, guildname), 'members')
    return False


@database_required
def unregister_guild(region, server, guildname):
    return g['redis'].srem('guilds', 'guild:{};{};{}'.format(region, server, guildname))


@client.event
async def on_ready():
    print("Logged in as")
    print(client.user.name)
    print(client.user.id)
    print('--------')


client.loop.create_task(refresh_guilds())
client.run(TOKEN)
