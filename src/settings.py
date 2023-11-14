import logging
import logging.config
import os
from pathlib import Path

import discord
import dotenv
from pony import orm
import yaml

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

with open(BASE_DIR / 'log_config.yml', encoding='utf-8') as logconfig:
    logging.config.dictConfig(yaml.safe_load(logconfig))

discord.utils.setup_logging(root=False)

discord.utils.setup_logging(root=False)

if not PROD:
    logging.info('Started debug mode.')

modules = [
    f'src.modules.{file.replace(".py", "")}'
    for file in os.listdir(BASE_DIR / 'src' / 'modules')
    if not file.startswith('_')
]

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
