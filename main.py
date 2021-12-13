import pathlib
import configparser

import discord
from discord.ext import commands
from pony.thirdparty.compiler.ast import Bitand

from src import stats
from src import birthday
from src import commands as com
from src import nsfw
from src.logger import pprint, log_in, logged_send
from src.custom_bot import CustomBot

ROOT_PATH = pathlib.Path(__file__).parent.absolute()
config = configparser.ConfigParser()
config.read(ROOT_PATH / 'config.ini')
bot = CustomBot(
    command_prefix=commands.when_mentioned_or('!'),
    intents=discord.Intents(members=True, messages=True, guilds=True),
    pm_help=True,
    default_channel=int(config['discord']['DEFAULT_CHANNEL']),
    default_server=int(config['discord']['DEFAULT_SERVER']))
TOKEN = config['discord']['TOKEN']


@bot.event
async def on_message(message):
    if not message.author.bot:
        stats.add_entry(message)
        if (message.content.startswith('!') and message.content[1:] != ''
            or message.content.startswith(f'<@!{bot.user.id}>') and message.content[len(f'<@!{bot.user.id}>'):] != ''):
            log_in(message)
        await bot.process_commands(message)


@bot.event
async def on_command_error(ctx, error):
    await logged_send(ctx, error)
    try:
        raise error
    except commands.errors.CommandNotFound:
        pass


@bot.event
async def on_ready():
    pprint(f'Logged in as {bot.user}.')
    pprint('---------')


bot.add_cog(com.DefaultCommands(bot))
bot.add_cog(nsfw.NSFWCommands(bot))
bot.add_cog(stats.StatsCommands(bot))
bot.add_cog(birthday.BirthdayCommands(bot))
bot.run(TOKEN)
