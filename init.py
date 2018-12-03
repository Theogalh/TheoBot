from autoredis import AutoRedis
import sys
import discord
import configparser
import argparse

g = dict()

config = configparser.ConfigParser()

if not config.read('conf.ini'):
    print("Error, no conf file.")
    sys.exit(1)

client = discord.Client()

try:
    g['redis'] = AutoRedis(('127.0.0.1', 6379),
                           password=None,
                           db=2,
                           decode_responses=True)
except (ConnectionError, KeyError):
    print('Error Database')
    sys.exit(-1)


class ArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise ValueError(message)

    def _print_message(self, message=None, file=None):
        if message:
            raise ValueError(message)

    def exit(self, status=0, message=None):
        print('TEST')
        print(message)
        pass
