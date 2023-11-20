from datetime import datetime

from pony import orm

from src.settings import database


class Message(database.Entity): # type: ignore
    id = orm.PrimaryKey(str)
    content = orm.Required(str)
    datetime = orm.Required(datetime)
    user_id = orm.Required(str)
    channel_id = orm.Required(str)
    server_id = orm.Required(str)

    def __repr__(self) -> str:
        return (
            f"<Message (id='{self.id}', content='{self.content[:20]}...', " +
            f"datetime='{self.datetime}', user_id='{self.user_id}', " +
            f"channel_id='{self.channel_id}', server_id='{self.server_id}')>"
        )

database.generate_mapping(create_tables=True)
