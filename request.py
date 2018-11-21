import requests
from app import g


def get_players(region, server, guild, split):
    guild_url = "https://www.wowprogress.com/rss/guild/{}/{}/{}/".format(region, server, guild)
    url = "https://api.rss2json.com/v1/api.json?rss_url={}".format(guild_url)
    req = requests.get(url)
    rep = ""
    separator = "----------------------------------------------------------"
    if req.status_code != 200:
        return "Error : Invalid guild name"

    content = req.json()

    for item in content["items"]:
        if split in item["title"]:
            url = item["description"].split('"')[9]
            Class = item["description"].split('"')[5]
            rep = "{}Name : {}\nWoW Progress URL = {}\nClass = {}\nGuild leaved : {}\n{}\n"\
                .format(rep, item["title"].split(" ")[0], url, Class, guild, separator)

    if rep == "":
        return "No leavers in this guild."
    return rep


def get_info(region, server, guild):

    guild_url = "https://www.wowprogress.com/rss/guild/{}/{}/{}/".format(region, server, guild)
    url = "https://api.rss2json.com/v1/api.json?rss_url={}".format(guild_url)
    req = requests.get(url)
    rep = ""
    separator = "----------------------------------------------------------"
    if req.status_code != 200:
        return "Error : Invalid guild name"

    content = req.json()

    for item in content["items"]:
        if split in item["title"]:
            url = item["description"].split('"')[9]
            Class = item["description"].split('"')[5]
            rep = "{}Name : {}\nWoW Progress URL = {}\nClass = {}\nGuild leaved : {}\n{}\n"\
                .format(rep, item["title"].split(" ")[0], url, Class, guild, separator)

    if rep == "":
        return "No leavers in this guild."
    return rep
