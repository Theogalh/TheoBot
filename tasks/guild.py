from init import client, config, g
import discord
import requests
import asyncio
from models.character import Character


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
        channel = discord.Object(id=config['DEFAULT']['CHANNEL_GUILD_ID'])
        msg = ''
        for guild in list:
            print("Guild {} on {}".format(guild.split(':')[3].capitalize(), guild.split(':')[2].capitalize()))
            url = 'https://{}.api.battle.net/wow/guild/{}/{}?fields=members&locale={}&apikey={}'.format(
                guild.split(':')[1],
                guild.split(':')[2],
                guild.split(':')[3],
                config['DEFAULT']['LOCALE'],
                config['DEFAULT']['BNET_APIKEY']
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
                    char.refresh()
                    if char.ilvl > int(config['DEFAULT']['ILVL_LIMIT']):
                        msg = msg + char.get_msg(True)
                    g['redis'].sadd('leavers', member)
                    g['redis'].srem('{}:members'.format(guild), member)
                    char.del_db()
            for member in new_members:
                if member not in old_members:
                    char = Character.from_db(name, member)
                    char.refresh()
                    if int(char.ilvl) > int(config['DEFAULT']['ILVL_LIMIT']):
                        msg = msg + char.get_msg(False)
                    g['redis'].sadd('{}:members'.format(guild), member)
                    g['redis'].srem('leavers', member)
        print("Refreshing Done.")
        if msg != '':
            await client.send_message(channel, msg)
        await asyncio.sleep(300)