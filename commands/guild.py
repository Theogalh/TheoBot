from init import config, g, client
from models.character import Character
from tasks.guild import get_new_members
import requests
LEVEL_MAX = 120


async def register_guild(server, guildname, message, allowed, **kwargs):
    server = server.capitalize()
    guildname = guildname.capitalize()
    if g['redis'].exists('guild:{}:{}:{}:members'.format(config['DEFAULT']['REGION'], server, guildname)):
        g['redis'].sadd('guilds', 'guild:{}:{}:{}'.format(config['DEFAULT']['REGION'], server, guildname))
        await client.send_message(message.channel, 'Guild {} is already followed.'.format(guildname))
        return
    url = 'https://{}.api.battle.net/wow/guild/{}/{}?fields=members&locale={}&apikey={}'.format(
        config['DEFAULT']['REGION'],
        server,
        guildname,
        config['DEFAULT']['LOCALE'],
        config['DEFAULT']['BNET_APIKEY']
    )
    rq = requests.get(url)
    if rq.status_code != 200:
        await client.send_message(message.channel, 'Guild {} does not exists.'.format(guildname))
    members = get_new_members(rq.json())
    g['redis'].sadd('guilds', 'guild:{}:{}:{}'.format(config['DEFAULT']['REGION'], server, guildname))
    for member in members:
        char = Character.from_db(guildname, member)
        if int(char.level) == LEVEL_MAX:
            g['redis'].sadd('guild:{}:{}:{}:members'.format(config['DEFAULT']['REGION'], server, guildname), member)
    await client.send_message(message.channel, 'Guild {} is now followed.'.format(guildname))


async def unregister_guild(server, guildname, message, allowed, **kwargs):
    server = server.capitalize()
    guildname = guildname.capitalize()
    g['redis'].srem('guilds', 'guild:{}:{}:{}'.format(config['DEFAULT']['REGION'], server, guildname))
    await client.send_message(message.channel, 'Guild {} is unfollowed.'.format(guildname))


async def info_guild(server, guildname, message, **kwargs):
    server = server.capitalize()
    guildname = guildname.capitalize()
    pass


async def list_leavers(message, **kwargs):
    leavers = g['redis'].smembers('leavers')
    if leavers:
        await client.send_message(message.channel, leavers)
    else:
        await client.send_message(message.channel, "No leavers at the moments")


def subparser_install(subparser):
    parser_guild_register = subparser.add_parser(
        'register',
        help='Register a guild for bot following'
    )
    parser_guild_register.set_defaults(func=register_guild)
    parser_guild_register.add_argument('server', help='The guild\'s server')
    parser_guild_register.add_argument('guildname', help='The guild\'s name')

    parser_guild_unregister = subparser.add_parser(
        'unregister',
        help='Unregister a guild followed by the bot'
    )
    parser_guild_unregister.set_defaults(func=unregister_guild)
    parser_guild_unregister.add_argument('server', help='The guild\'s server')
    parser_guild_unregister.add_argument('guildname', help='The guild\'s name')

    parser_guild_info = subparser.add_parser(
        'info',
        help='Unregister a guild followed by the bot'
    )
    parser_guild_info.set_defaults(func=info_guild)
    parser_guild_info.add_argument('server', help='The guild\'s server')
    parser_guild_info.add_argument('guildname', help='The guild\'s server')

    parser_guild_leavers = subparser.add_parser(
        'leavers',
        help='List the player who leaves the guilds followed.'
    )
    parser_guild_leavers.set_defaults(func=list_leavers)
