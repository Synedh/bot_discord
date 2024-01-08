import logging
import typing
from datetime import date, datetime, time, timezone

import discord
import pytz
from discord.ext import commands, tasks
from pony import orm

from src.errors import ForbiddenOperation, GuildOperation, ParameterError
from .models import Birthday

if typing.TYPE_CHECKING:
    from src.this_is_the_bot import ThisIsTheBot

MODULE_NAME = "Birthdays"

tz = timezone(pytz.timezone('Europe/Paris').utcoffset(datetime.now()))
DAILY_SHOUT_TIME = time(hour=0, minute=0, tzinfo=tz)


class Commands(commands.Cog, name=MODULE_NAME):
    def __init__(self, bot: 'ThisIsTheBot'):
        self.bot = bot
        self.daily_shout.start()

    def cog_unload(self):
        self.daily_shout.cancel()

    @commands.hybrid_group() # type: ignore
    async def birthday(self, _: commands.Context['ThisIsTheBot']) -> None:
        """Birthday commands."""

    @birthday.command() # type: ignore
    async def list(self, ctx: commands.Context['ThisIsTheBot']) -> None:
        """Display registered birthdays"""
        if not ctx.guild:
            raise GuildOperation()
        now = datetime.now().date()
        birthdays = []
        with orm.db_session:
            for birthday in Birthday.select():
                delta1 = date(now.year, birthday.birth_date.month, birthday.birth_date.day)
                delta2 = date(now.year + 1, birthday.birth_date.month, birthday.birth_date.day)
                age = int(round(((delta1 if delta1 >= now else delta2) - birthday.birth_date.date()).days / 365.25))
                next_days = ((delta1 if delta1 >= now else delta2) - now).days
                next_str = (
                    'aujourd\'hui' if next_days == 0 else
                    'demain' if next_days == 1 else
                    f'dans {next_days} jours'
                )
                user = ctx.guild.get_member(int(birthday.user_id))

                birthdays.append({
                    'user': user.mention if user else '<deleted>',
                    'date': birthday.birth_date.strftime("%d %b %Y"),
                    'next_days': next_days,
                    'next': next_str,
                    'age': age,
                })

        birthdays.sort(key=lambda birthday: birthday['next_days'])
        birthday_list = [
            f'- {birthday["user"]}: {birthday["date"]} ({birthday["age"]} ans {birthday["next"]})'
            for birthday in birthdays
        ]

        embed = discord.Embed(
            title='Liste des anniversaires enregistrés',
            description='\n'.join(birthday_list),
            color=discord.Color.blue()
        )
        await self.bot.send(ctx, embed=embed)


    @birthday.command() # type: ignore
    async def add(
        self,
        ctx: commands.Context['ThisIsTheBot'],
        birthday: str,
        user: discord.User | discord.Member | None = None
    ) -> None:
        """Add birthday for current or given user"""
        if not ctx.guild:
            raise GuildOperation()
        if ctx.author not in (user, ctx.guild.owner):
            raise ForbiddenOperation()
        if not user:
            user = ctx.author
        try:
            birthdate = datetime.strptime(birthday, '%d-%m-%Y')
            if (datetime.now() - birthdate).days < 365.25 * 15:
                raise ParameterError('Incorrect date, too young to be here !')
        except ValueError as error:
            raise ParameterError('Incorrect date format, please use DD-MM-YYYY format') from error

        with orm.db_session:
            query = Birthday.select(lambda birthdate: birthdate.user_id == user.id)
            if query.count() > 0:
                query.first().birth_date = birthdate
                description = f'Birthdate has been udpated for {user.mention}.'
            else:
                _ = Birthday(
                    user_id=str(user.id),
                    birth_date=birthdate
                )
                description = f'Birthdate has been added for {user.mention}.'
            orm.commit()
        await self.bot.send(ctx, description, color=discord.Color.green())


    @birthday.command() # type: ignore
    async def remove(
        self,
        ctx: commands.Context['ThisIsTheBot'],
        user: discord.User | discord.Member | None = None
    ) -> None:
        """Remove birthday for current or given user"""
        if not ctx.guild:
            raise GuildOperation()
        if ctx.author not in (user, ctx.guild.owner):
            raise ForbiddenOperation()
        if not user:
            user = ctx.author

        with orm.db_session:
            _ = Birthday.select(lambda birthdate: birthdate.user_id == user.id).first().delete()
            orm.commit()

        await self.bot.send(ctx, f'Birthdate has been removed for {user.mention}.')

    @tasks.loop(time=DAILY_SHOUT_TIME)
    async def daily_shout(self) -> None:
        """Shout birthdays for current date"""
        await self.bot.wait_until_ready()
        now = datetime.now()

        with orm.db_session:
            query = Birthday.select(lambda birthday: (
                birthday.birth_date.day == now.day and
                birthday.birth_date.month == now.month
            ))
            if query.count() == 0:
                return
            birthdays = [
                f'<@{birthday.user_id}> ({now.year - birthday.birth_date.year} ans)'
                for birthday in query
            ]

        text = 'Aujourd\'hui, c\'est l\'anniversaire de '
        if len(birthdays) > 1:
            text += f'{", ".join(birthdays[:-1])} et {birthdays[-1]}'
        else:
            text += birthdays[0]
        await self.bot.send(content=text + ' !\n\nFêtez ça comme il se doit ! :partying_face:')


async def setup(bot: 'ThisIsTheBot') -> None:
    await bot.add_cog(Commands(bot))
    logging.info('Loaded module %s.', MODULE_NAME)
