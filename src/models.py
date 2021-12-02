import pathlib
import configparser
from datetime import datetime

from pony import orm

from .logger import pprint

ROOT_PATH = pathlib.Path(__file__).parent.parent.absolute()
config = configparser.ConfigParser()
config.read(ROOT_PATH / 'config.ini')

try:
    prod = config['config']['TYPE'] != 'DEBUG'
    pprint('Start in debug mode.')
except KeyError:
    prod = True
if prod:
    db = orm.Database(provider='sqlite', filename=str(ROOT_PATH / 'db.sqlite'), create_db=True)
else:
    db = orm.Database(provider='sqlite', filename=':memory:')

class Message(db.Entity):
    id = orm.PrimaryKey(str)
    content = orm.Required(str)
    datetime = orm.Required(datetime)
    user_id = orm.Required(str)
    channel_id = orm.Required(str)
    server_id = orm.Required(str)

    def __repr__(self):
        return f"<Message (id='{self.id}', content='{self.content[:20]}...', datetime='{self.datetime}', user_id='{self.user_id}', channel_id='{self.channel_id}', server_id='{self.server_id}')>"


class Birthday(db.Entity):
    user_id = orm.Required(str, unique=True)
    birth_date = orm.Required(datetime)
    last_birthday = orm.Optional(int)

    def __repr__(self):
        return f'<Birthday (user_id="{self.user_id}", birth_date="{self.birth_date}", last_birthday="{self.last_birthday}")>'

db.generate_mapping(create_tables=True)
