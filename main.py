import json
import logging
import logging.config
import os
from pathlib import Path

import discord
import dotenv
from discord.ext import commands

from src.this_is_the_bot import ThisIsTheBot

BASE_DIR = Path(__file__).resolve().parent
dotenv.load_dotenv(BASE_DIR / '.env')

assert os.getenv('TOKEN') is not None
assert os.getenv('PREFIX') is not None
assert os.getenv('DEFAULT_CHANNEL') is not None
assert os.getenv('DEFAULT_SERVER') is not None

TOKEN = str(os.getenv('TOKEN'))
PREFIX = str(os.getenv('PREFIX'))
DEFAULT_CHANNEL = int(str(os.getenv('DEFAULT_CHANNEL')))
DEFAULT_SERVER = int(str(os.getenv('DEFAULT_SERVER')))

with open(BASE_DIR / 'log_config.json', encoding='utf-8') as logconfig:
    logging.config.dictConfig(json.load(logconfig))

bot = ThisIsTheBot(
    command_prefix=commands.when_mentioned_or(PREFIX),
    intents=discord.Intents(members=True, message_content=True, messages=True, guilds=True),
    pm_help=True,
    default_channel=DEFAULT_CHANNEL,
    default_server=DEFAULT_SERVER,
)

modules = [
    f'src.modules.{file[:-3]}'
    for file in os.listdir(BASE_DIR / 'src' / 'modules')
    if not file.startswith('_')
]

@bot.event
async def on_ready() -> None:
    logging.info('Logged in as %s.', bot.user)
    for module in modules:
        await bot.load_extension(module)

bot.run(TOKEN)
