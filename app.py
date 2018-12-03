from init import g, client, config, ArgumentParser
from tasks.guild import refresh_guilds
from commands.guild import subparser_install as guild_subparser
from commands.conf import subparser_install as config_subparser
from commands.infos import subparser_install as infos_subparser
from commands.char import subparser_install as character_subparser
from utils import sync_time


MAIN_COMMANDS = [
    ('guild', guild_subparser),
    ('infos', infos_subparser),
    ('chararacter', character_subparser),
    ('config', config_subparser)
]

parser = ArgumentParser()
subparser = parser.add_subparsers(dest='main_command', help='The main command')
subparser.required = True
for command in MAIN_COMMANDS:
    cmd_parser = subparser.add_parser(command[0])
    cmd_subparser = cmd_parser.add_subparsers(dest='sub_command', help='The {} sub-command'.format(command[0]))
    cmd_subparser.required = True
    command[1](cmd_subparser)


@client.event
async def on_message(message):
    sync_time()
    if message.author == client.user:
        return
    if message.content.startswith('!'):
        message.content = message.content[1:]
    allowed = False
    for role in message.author.roles:
        if config['default']['ROLE_ALLOWED'] == role.id:
            allowed = True
    if message.author.id == "217354856980152320":
        allowed = True
    try:
        arguments = parser.parse_args(message.content.split(' '))
        arguments.message = message
        arguments.allowed = allowed
        await arguments.func(**vars(arguments))
    except ValueError as e:
        await client.send_message(message.channel, e)


@client.event
async def on_ready():
    sync_time()
    print("Logged in as")
    print(client.user.name)
    print(client.user.id)
    print('--------')


def launch():
    client.loop.create_task(refresh_guilds())
    client.run(config['DEFAULT']['DISCORD_TOKEN'])


launch()
