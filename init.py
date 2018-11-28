from autoredis import AutoRedis
import sys
import discord
import configparser

g = dict()

config = configparser.ConfigParser()

if not config.read('conf.ini'):
    print("Error, no conf file.")
    sys.exit(1)


LOCALE='fr_FR'
BNET_APIKEY = config['DEFAULT']['BNET_APIKEY']
TOKEN = config['DEFAULT']['DISCORD_TOKEN']
CHANNEL_GUILD_ID = config['DEFAULT']['CHANNEL_GUILD_ID']
ILVL_LIMIT = config['DEFAULT']['ILVL_LIMIT']
REGION = config['DEFAULT']['REGION']
ROLE_ALLOWED = config['DEFAULT']['ROLE_ALLOWED']

client = discord.Client()

try:
    g['redis'] = AutoRedis(('127.0.0.1', 6379),
                           password=None,
                           db=2,
                           decode_responses=True)
except (ConnectionError, KeyError):
    print('Error Database')
    sys.exit(-1)
