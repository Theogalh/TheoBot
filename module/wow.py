from init import REGION as APIREGION, ILVL_LIMIT, CHANNEL_GUILD_ID, client


def subparser_install(subparser):
    parser_wow_info = subparser.add_parser(
        'info',
        help='Get WoW Bot informations'
    )
    parser_wow_info.set_defaults(func=wow_info)


def wow_info(message, **kwargs):
    msg = "Hello {}\n".format(message.author.mention)
    msg = msg + 'Region : {}\n' \
                'Ilvl Limit : {}\n' \
                'Channel : {}\n' \
                'Guilds registered : '.format(APIREGION,
                                              ILVL_LIMIT,
                                              CHANNEL_GUILD_ID)
    for guild in g['redis'].smembers('guilds'):
        msg = msg + '{}, '.format(guild.split(':')[3].capitalize())
    return msg


MAIN_COMMANDS = [
    ('!wow', wow_subparser),
    ('!ping')
]

from module.wow import wow_subparser


parser = argparse.ArgumentParser(description='Theogalh \' Discord Bot.')
subparser = parser.add_subparsers(dest='main_command', help='The main command')
subparser.required = True
for command in MAIN_COMMANDS:
    cmd_parser = subparser.add_parser(command[0])
    cmd_subparser = cmd_parser.add_subparsers(dest='sub_command', help='The {} sub-command'.format(command[0]))
    cmd_subparser.required = True
    command[1](cmd_subparser)