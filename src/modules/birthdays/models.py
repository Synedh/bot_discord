from datetime import datetime

from pony import orm

from src.settings import database


class Birthday(database.Entity): #type: ignore
    user_id = orm.Required(str, unique=True)
    birth_date = orm.Required(datetime)
    last_birthday = orm.Optional(int)

    def __repr__(self) -> str:
        return (
            f'<Birthday (user_id="{self.user_id}", birth_date="{self.birth_date}", ' +
            f'last_birthday="{self.last_birthday}")>'
        )
