import pathlib
import configparser
from discord.ext import commands

from src import stats
from src import commands as com
from src.models import Message
from src.logging import log_in, log_out

ROOT_PATH = pathlib.Path(__file__).parent.absolute()
config = configparser.ConfigParser()
config.read(ROOT_PATH / 'config.ini')
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
    log_in(ctx)


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
