from pony import orm
from discord.ext import commands
from datetime import datetime, timedelta

from models import Message

class StatsCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def stats(self, ctx, detail: str=None):
        """Get stats of given server. Use @user or #channel for details."""
        if not detail:
            await ctx.send(week_stats(ctx.message.guild.id))
        elif detail[1] == '@':
            await ctx.send(user_stats(ctx.message.guild.id, detail[2:-1]))
        elif detail[1] == '#':
            await ctx.send(channel_stats(ctx.message.guild.id, detail[2:-1]))
        else:
            await ctx.send(f'Invalid given value "{detail}". Please tag a channel or a user.')


@orm.db_session
def add_entry(message):
    _ = Message(
        id=str(message.id),
        content=message.content,
        datetime=datetime.now(),
        user_id=str(message.author.id),
        channel_id=str(message.channel.id),
        server_id=str(message.guild.id)
    )
    orm.commit()


@orm.db_session
def week_stats(server_id):
    last_week = datetime.now() - timedelta(days=7)
    user_stats = {}
    channel_stats = {}

    query = Message.select(lambda m: m.server_id == server_id and m.datetime >= last_week and m.channel_id != '433665712247144463')
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


@orm.db_session
def user_stats(server_id, user_id):
    date_stats = {}
    channel_stats = {}

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


@orm.db_session
def channel_stats(server_id, channel_id):
    date_stats = {}
    user_stats = {}

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
