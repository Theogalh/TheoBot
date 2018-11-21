import requests
import sys


def get_leavers(region, server, guild):
    guild_url = "https://www.wowprogress.com/rss/guild/{}/{}/{}/".format(region, server, guild)
    url = "https://api.rss2json.com/v1/api.json?rss_url={}".format(guild_url)
    req = requests.get(url)
    rep = ""
    separator = "----------------------------------------------------------"
    if req.status_code != 200:
        print("Error : Invalid guild name")
        return
    content = req.json()

    for item in content["items"]:
        if "left" in item["title"]:
            url = item["description"].split('"')[9]
            Class = item["description"].split('"')[5]
            rep = "{}Name : {}\nWoW Progress URL = {}\nClass = {}\nGuild leaved : {}\n{}\n"\
                .format(rep, item["title"].split(" ")[0], url, Class, guild, separator)
    return rep


print(get_leavers(sys.argv[1], sys.argv[2], sys.argv[3]))
