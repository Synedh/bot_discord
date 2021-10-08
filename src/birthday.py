from pony import orm
from discord.ext import commands
from datetime import datetime

from .models import Birthday
from .logger import logged_send

SYNEDH_USER_ID = 114880864772423682

class BirthdayCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def birthday(self, ctx, cmd: str=None, date: str=None, user_id: str=None):
        """Manage birthdays. Use `list` to show registered dates, `add` to add or `rm` to `remove`."""
        if cmd == 'list':
            await logged_send(ctx, await list_birthdates(self.bot))
        elif cmd == 'add':
            if user_id and ctx.message.author.id == SYNEDH_USER_ID:
                await logged_send(ctx, add_birthdate(user_id, date))
            else:
                await logged_send(ctx, add_birthdate(ctx.message.author.id, date))
        elif cmd == 'rm':
            if date and ctx.message.author.id == SYNEDH_USER_ID:
                await logged_send(ctx, rm_birthdate(date))
            else:
                await logged_send(ctx, rm_birthdate(ctx.message.author.id))
        else:
            await logged_send(ctx, f'Invalid given command "{cmd}". Use `list` to show registered dates, `add` to add or `rm` to remove.')


@orm.db_session
async def list_birthdates(bot):
    query = Birthday.select()
    birthdays = [{
        'user': await bot.fetch_user(birthdate.user_id),
        'date': birthdate.birth_date.strftime("%d-%m-%Y")
    } for birthdate in query]
    return (
        'Liste des anniversaires enregistrés sur ce serveur :\n\n' +
        '\n'.join([f'- {birthdate["user"]} - {birthdate["date"]}' for birthdate in birthdays])
    )


@orm.db_session
def add_birthdate(user_id, date):
    try:
        date = datetime.strptime(date, '%d-%m-%Y')
    except ValueError:
        return 'Incorrect date format, please use DD-MM-YYYY format'
    query = Birthday.select(lambda birthdate: birthdate.user_id == user_id)
    if query.count() > 0:
        query.first().birth_date = date
        orm.commit()
        return f'Birthdate has been udpated for user <@{user_id}>.'
    Birthday(user_id=str(user_id), birth_date=date)
    orm.commit()
    return f'Birthdate has been added for user <@{user_id}>.'


@orm.db_session
def rm_birthdate(user_id):
    Birthday.select(lambda birthdate: birthdate.user_id == user_id).first().delete()
    orm.commit()
    return f'Birthdate has been removed for user <@{user_id}>.'
