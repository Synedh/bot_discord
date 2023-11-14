import json
import logging
import logging.config
import os
from pathlib import Path

import discord
import dotenv
from discord.ext import commands
from pony import orm

from src.this_is_the_bot import ThisIsTheBot

BASE_DIR = Path(__file__).resolve().parent.parent
dotenv.load_dotenv(BASE_DIR / '.env')

assert os.getenv('PROD') is not None
assert os.getenv('TOKEN') is not None
assert os.getenv('PREFIX') is not None
assert os.getenv('DEFAULT_CHANNEL') is not None
assert os.getenv('DEFAULT_SERVER') is not None

PROD = str(os.getenv('PROD')) == 'True'
TOKEN = str(os.getenv('TOKEN'))
PREFIX = str(os.getenv('PREFIX'))
DEFAULT_CHANNEL = int(str(os.getenv('DEFAULT_CHANNEL')))
DEFAULT_SERVER = int(str(os.getenv('DEFAULT_SERVER')))

with open(BASE_DIR / 'log_config.json', encoding='utf-8') as logconfig:
    logging.config.dictConfig(json.load(logconfig))

discord.utils.setup_logging(root=False)

if not PROD:
    logging.info('Started debug mode.')

modules = [
    f'src.modules.{file.replace('.py', '')}'
    for file in os.listdir(BASE_DIR / 'src' / 'modules')
    if not file.startswith('_')
]

bot = ThisIsTheBot(
    modules=modules,
    command_prefix=commands.when_mentioned_or(PREFIX),
    intents=discord.Intents.all(),
    pm_help=True,
    default_channel=DEFAULT_CHANNEL,
    default_server=DEFAULT_SERVER,
)

if PROD:
    database = orm.Database(
        provider='sqlite',
        filename=str(BASE_DIR / 'db.sqlite'),
        create_db=True
    )
else:
    database = orm.Database(
        provider='sqlite',
        filename=':memory:'
    )
