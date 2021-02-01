import pathlib
import configparser
from discord.ext import commands

import stats
import commands as com
from models import Message

config = configparser.ConfigParser()
config.read(pathlib.Path(__file__).parent.absolute() / 'config.ini')
bot = commands.Bot(command_prefix=commands.when_mentioned_or('!'), pm_help=True)
TOKEN = config['discord']['token']


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    stats.add_entry(message)
    await bot.process_commands(message)


@bot.event
async def on_command(ctx):
    print(ctx.message.content)


@bot.event
async def on_command_error(ctx, error):
    await ctx.send(error)
    raise error


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}.')
    print('---------')


bot.add_cog(com.DefaultCommands(bot))
bot.add_cog(stats.StatsCommands(bot))
bot.run(TOKEN)
