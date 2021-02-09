from pony import orm
from datetime import datetime

# db = orm.Database(provider='sqlite', filename=':memory:')
db = orm.Database(provider='sqlite', filename='../db.sqlite', create_db=True)

class Message(db.Entity):
    id = orm.PrimaryKey(str)
    content = orm.Required(str)
    datetime = orm.Required(datetime)
    user_id = orm.Required(str)
    channel_id = orm.Required(str)
    server_id = orm.Required(str)

    def __repr__(self):
        return f"<Message (id='{self.id}', content='{self.content[:20]}...', datetime='{self.datetime}', user_id='{self.user_id}', channel_id='{self.channel_id}', server_id='{self.server_id}')>"

db.generate_mapping(create_tables=True)
