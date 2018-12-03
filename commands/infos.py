from init import config, client, g


def subparser_install(subparser):
    parser_info_all = subparser.add_parser(
        'all',
        help='Get all infos from the Bot.'
    )
    parser_info_all.set_defaults(func=get_all_infos)
    parser_info_ping = subparser.add_parser(
        'ping',
        help='Test if bot works'
    )
    parser_info_ping.set_defaults(func=ping)


async def get_all_infos(message, **kwargs):
    msg = "Hello {}\n".format(message.author.mention)
    msg = msg + 'Region : {}\n' \
                'Ilvl Limit : {}\n' \
                'Channel : {}\n' \
                'Guilds registered : '.format(config['DEFAULT']['REGION'],
                                              config['DEFAULT']['ILVL_LIMIT'],
                                              config['DEFAULT']['CHANNEL_GUILD_ID'])
    for guild in g['redis'].smembers('guilds'):
        msg = msg + '{}, '.format(guild.split(':')[3].capitalize())
    await client.send_message(message.channel, msg)


async def ping(message, **kwargs):
    await client.send_message(message.channel, '{} Pong'.format(message.author.mention))
