from datetime import datetime, timedelta
import logging

from discord.ext import commands
from pony import orm

from .models import Message
from src.this_is_the_bot import ThisIsTheBot

MODULE_NAME = "Stats"


class StatsCommands(commands.Cog, name=MODULE_NAME):
    def __init__(self, bot: ThisIsTheBot):
        self.bot = bot

    @commands.hybrid_command() # type: ignore
    async def stats(self, ctx: commands.Context[ThisIsTheBot], detail: str | None=None) -> None:
        """Get stats of given server. Use @user or #channel for details."""
        guild_id = ctx.message.guild.id if ctx.message.guild else -1
        if not detail:
            message = week_stats(guild_id)
        elif detail[1] == '@':
            message = user_stats(guild_id, detail[2:-1])
        elif detail[1] == '#':
            message = channel_stats(guild_id, detail[2:-1])
        else:
            message = f'Invalid given value "{detail}". Please tag a channel or a user.'
        await self.bot.send(ctx, message)


@orm.db_session # type: ignore
def add_entry(message: Message) -> None:
    _ = Message(
        id=str(message.id),
        content=message.content,
        datetime=datetime.now(),
        user_id=str(message.author.id),
        channel_id=str(message.channel.id),
        server_id=str(message.guild.id)
    )
    orm.commit()


@orm.db_session # type: ignore
def week_stats(server_id: int) -> str:
    last_week = datetime.now() - timedelta(days=7)
    user_stats: dict[str, int] = {}
    channel_stats: dict[str, int] = {}

    query = Message.select(lambda m: m.server_id == server_id and m.datetime >= last_week and m.channel_id not in ['433665712247144463', '916071520554614785'])
    for message in query:
        user_stats[message.user_id] = user_stats.get(message.user_id, 0) + 1
        channel_stats[message.channel_id] = channel_stats.get(message.channel_id, 0) + 1
    ordered_user_stats = sorted(list(user_stats.items()), key=lambda v: v[1], reverse=True)
    ordered_channel_stats = sorted(list(channel_stats.items()), key=lambda v: v[1], reverse=True)
    user_detail = '\n'.join(['- <@%s> : %d' % stats for stats in ordered_user_stats[:10]])
    channel_detail = '\n'.join(['- <#%s> : %d' % stats for stats in ordered_channel_stats[:5]])

    return ((
        '%d messages envoyés les 7 derniers jours.\n\n' +
        'Les plus gros posteurs des 7 derniers jours :\n%s\n\n' +
        'Les canaux des 7 derniers jours :\n%s') %
        (sum(user_stats.values()), user_detail, channel_detail)
    )


@orm.db_session # type: ignore
def user_stats(server_id: int, user_id: int):
    date_stats: dict[str, int] = {}
    channel_stats: dict[str, int] = {}

    query = Message.select(lambda m: m.server_id == server_id and m.user_id == user_id and m.channel_id != '433665712247144463')
    for message in query:
        if message.datetime > datetime.now() - timedelta(days=7):
            channel_stats[message.channel_id] = channel_stats.get(message.channel_id, 0) + 1
        date = message.datetime.strftime('%W-%Y')
        date_stats[date] = date_stats.get(date, 0) + 1

    ordered_channel_stats = sorted(list(channel_stats.items()), key=lambda v: -v[1])[:5]
    ordered_date_stats = [(stats[0].split('-')[0], stats[1]) for stats in reversed(list(date_stats.items())[-5:])]
    channel_detail = '\n'.join(['- <#%s> : %d' % stats for stats in ordered_channel_stats])
    date_detail = '\n'.join([' - Semaine %s : %d' % stats for stats in ordered_date_stats])

    return ((
        '<@%s> a posté %d messages les 7 derniers jours.\n\n' +
        'Canaux favoris :\n%s\n\n' +
        'Historique des dernières semaines :\n%s') %
        (user_id, sum(channel_stats.values()), channel_detail, date_detail)
    )


@orm.db_session # type: ignore
def channel_stats(server_id: int, channel_id: int):
    date_stats: dict[str, int] = {}
    user_stats: dict[str, int] = {}

    query = Message.select(lambda m: m.server_id == server_id and m.channel_id == channel_id)
    for message in query:
        if message.datetime > datetime.now() - timedelta(days=7):
            user_stats[message.user_id] = user_stats.get(message.user_id, 0) + 1
        date = message.datetime.strftime('%W-%Y')
        date_stats[date] = date_stats.get(date, 0) + 1

    ordered_user_stats = sorted(list(user_stats.items()), key=lambda v: -v[1])[:10]
    ordered_date_stats = [(stats[0].split('-')[0], stats[1]) for stats in reversed(list(date_stats.items())[-5:])]
    user_detail = '\n'.join(['- <@%s> : %d' % stats for stats in ordered_user_stats])
    date_detail = '\n'.join([' - Semaine %s : %d' % stats for stats in ordered_date_stats])

    return ((
        '%d messages ont étés postés les 7 derniers jours dans <#%s>\n\n' +
        'Les plus gros posteurs des 7 derniers jours :\n%s\n\n' +
        'Historique des dernières semaines :\n%s') %
        (sum(user_stats.values()), channel_id, user_detail, date_detail)
    )


async def setup(bot: ThisIsTheBot) -> None:
    await bot.add_cog(StatsCommands(bot))
    logging.info('Loaded module %s.', MODULE_NAME)
