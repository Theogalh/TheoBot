from autoredis import AutoRedis
from functools import wraps
import sys
import discord
from request import get_players

g = dict()
TOKEN = 'NTE0ODc1MDE0NzU2MTcxNzc4.Dtc6eQ.wXWKicjAC3o_sZN76C7LLbQxKws'

client = discord.Client()


def database_open():
    try:
        g['redis'] = AutoRedis(('127.0.0.1', 6379),
                               password=None,
                               db=5,
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


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    g['redis'].sadd('theobot:history', message.content)

    if message.content.startswith('!hello'):
        msg = "Hello {}".format(message.author.mention)
        await client.send_message(message.channel, msg)

    if message.content.startswith('!guild'):
        args = message.content.split(' ')
        if len(args) != 4:
            await client.send_message(message.channel, "Error, need !guild <region> <server> <guildname>")
        else:
            await client.send_message(message.channel, get_players(args[1], args[2], args[3], "left"))


@client.event
async def on_ready():
    print("Logged in as")
    print(client.user.name)
    print(client.user.id)
    print('--------')


@database_required
def launch():
    client.run(TOKEN)

launch()
