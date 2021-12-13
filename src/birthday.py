from pony import orm
from discord.ext import commands
from datetime import date, datetime

from .models import Birthday
from .logger import logged_send

SYNEDH_USER_ID = 114880864772423682

class BirthdayCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def birthday(self, ctx, cmd: str=None, date: str=None, user_id: str=None):
        """Manage brithdays. Use `list` to show registered dates, `add` to add, `rm` to `remove` or `shout` to ping birthdays."""
        if cmd == 'list':
            await logged_send(ctx, list_birthdates(ctx.message.guild))
        elif cmd == 'add':
            if user_id and ctx.message.author.id == SYNEDH_USER_ID:
                await logged_send(ctx, add_birthdate(ctx.message.guild.get_member(int(user_id)), date))
            else:
                await logged_send(ctx, add_birthdate(ctx.message.author, date))
        elif cmd == 'rm':
            if date and ctx.message.author.id == SYNEDH_USER_ID:
                await logged_send(ctx, rm_birthdate(ctx.message.guild.get_member(int(date))))
            else:
                await logged_send(ctx, rm_birthdate(ctx.message.author))
        elif cmd == 'shout':
            await logged_send(ctx, send_birthdays())
        else:
            await logged_send(ctx, f'Invalid given command "{cmd}". Use `list` to show registered dates, `add` to add, `rm` to remove or `shout` to ping birthdays.')


@orm.db_session
def list_birthdates(guild):
    now = datetime.now().date()
    birthdays = []
    for birthday in Birthday.select():
        delta1 = date(now.year, birthday.birth_date.month, birthday.birth_date.day)
        delta2 = date(now.year + 1, birthday.birth_date.month, birthday.birth_date.day)
        next_days = ((delta1 if delta1 >= now else delta2) - now).days

        birthdays.append({
            'user': guild.get_member(int(birthday.user_id)).name,
            'date': birthday.birth_date.strftime("%d %b %Y"),
            'next_days': next_days,
            'next': 'aujourd\'hui' if next_days == 0 else 'demain' if next_days == 1 else f'dans {next_days} jours',
            'age': int(round(((delta1 if delta1 >= now else delta2) - birthday.birth_date.date()).days / 365.25)),
        })
    birthdays.sort(key=lambda birthday: birthday['next_days'])
    return (
        'Liste des anniversaires enregistrés sur ce serveur :\n\n' +
        '\n'.join([f'- {birthday["user"]}: {birthday["date"]} ({birthday["age"]} ans {birthday["next"]})' for birthday in birthdays])
    )


@orm.db_session
def add_birthdate(user, date):
    try:
        date = datetime.strptime(date, '%d-%m-%Y')
        if (datetime.now() - date).days < 365.25 * 15:
            return 'Incorrect date, too young to be here !'
    except ValueError:
        return 'Incorrect date format, please use DD-MM-YYYY format'
    query = Birthday.select(lambda birthdate: birthdate.user_id == user.id)
    if query.count() > 0:
        query.first().birth_date = date
        orm.commit()
        return f'Birthdate has been udpated for {user.name}.'
    _ = Birthday(
        user_id=str(user.id),
        birth_date=date
    )
    orm.commit()
    return f'Birthdate has been added for {user.name}.'


@orm.db_session
def rm_birthdate(user):
    _ = Birthday.select(lambda birthdate: birthdate.user_id == user.id).first().delete()
    orm.commit()
    return f'Birthdate has been removed for {user.name}.'


@orm.db_session
def send_birthdays(auto=False):
    now = datetime.now()
    if auto:
        query = Birthday.select(lambda birthday: (
            birthday.birth_date.day == now.day 
            and birthday.birth_date.month == now.month 
            and (not birthday.last_birthday or birthday.last_birthday != now.year)
        ))
        if query.count() == 0:
            return
    else:
        query = Birthday.select(lambda birthday: birthday.birth_date.day == now.day and birthday.birth_date.month == now.month)
        if query.count() == 0:
            return 'Pas d\'anniversaire aujourd\'hui :\'('

    birthdays = [f'<@{birthday.user_id}> ({now.year - birthday.birth_date.year} ans)' for birthday in query]
    for birthday in query:
        birthday.last_birthday = now.year
    orm.commit()

    text = f'Aujourd\'hui, c\'est l\'anniversaire de '
    if len(birthdays) > 1:
        text += f'{", ".join(birthdays[:-1])} et {birthdays[-1]}'
    else:
        text += birthdays[0]
    return text + ' !\n\nFêtez ça comme il se doit ! :partying_face:'
