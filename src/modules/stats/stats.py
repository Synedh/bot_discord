import logging
import typing
from datetime import datetime, timedelta, time, timezone

import discord
import pytz
from discord.ext import commands, tasks
from pony import orm

from .models import Message

if typing.TYPE_CHECKING:
    from src.this_is_the_bot import ThisIsTheBot

MODULE_NAME = "Stats"

tz = timezone(pytz.timezone('Europe/Paris').utcoffset(datetime.now()))
DAILY_SHOUT_TIME = time(hour=9, minute=0, tzinfo=tz)


class Commands(commands.Cog, name=MODULE_NAME):
    def __init__(self, bot: 'ThisIsTheBot'):
        self.bot = bot
        self.shout_weekly_stats.start()

    def cog_unload(self):
        self.shout_weekly_stats.cancel()

    @commands.hybrid_group() # type: ignore
    async def stats(self, _: commands.Context['ThisIsTheBot']) -> None:
        """Stats commands"""

    @stats.command() # type: ignore
    async def week(self, ctx: commands.Context['ThisIsTheBot']) -> None:
        """Weekly stats"""
        embed = from_date_stats(ctx.message.guild, datetime.now() - timedelta(days=7))
        await self.bot.send(ctx, embed=embed)

    @stats.command() # type: ignore
    async def month(self, ctx: commands.Context['ThisIsTheBot']) -> None:
        """Monthly stats"""
        embed = from_date_stats(ctx.message.guild, datetime.now() - timedelta(days=31))
        await self.bot.send(ctx, embed=embed)

    @stats.command() # type: ignore
    async def year(self, ctx: commands.Context['ThisIsTheBot']) -> None:
        """Yearly stats"""
        embed = from_date_stats(ctx.message.guild, datetime.now() - timedelta(days=365))
        await self.bot.send(ctx, embed=embed)

    @stats.command() # type: ignore
    async def user(self, ctx: commands.Context['ThisIsTheBot'], user: discord.Member) -> None:
        """User weekly stats"""
        embed = user_stats(ctx.message.guild, user)
        await self.bot.send(ctx, embed=embed)

    @stats.command() # type: ignore
    async def channel(
        self,
        ctx: commands.Context['ThisIsTheBot'],
        channel: discord.TextChannel | discord.VoiceChannel | discord.Thread
    ) -> None:
        """Channel weekly stats"""
        embed = channel_stats(ctx.message.guild, channel)
        await self.bot.send(ctx, embed=embed)

    @tasks.loop(time=DAILY_SHOUT_TIME)
    async def shout_weekly_stats(self):
        if datetime.now().weekday() != 0:
            return
        await self.bot.wait_until_ready()
        server = self.bot.get_guild(self.bot.default_server)
        embed = from_date_stats(server, datetime.now() - timedelta(days=7))
        await self.bot.send(embed=embed)


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
def from_date_stats(server: discord.Guild, date: datetime) -> discord.Embed:
    usr_stats: dict[str, int] = {}
    chan_stats: dict[str, int] = {}

    query = Message.select(lambda m: (
        m.server_id == server.id and
        m.datetime >= date and
        m.channel_id not in ['433665712247144463', '916071520554614785']
    ))
    for message in query:
        usr_stats[message.user_id] = usr_stats.get(message.user_id, 0) + 1
        chan_stats[message.channel_id] = chan_stats.get(message.channel_id, 0) + 1
    ordered_usr_stats = sorted(usr_stats.items(), key=lambda v: v[1], reverse=True)
    ordered_channel_stats = sorted(chan_stats.items(), key=lambda v: v[1], reverse=True)
    user_detail = '\n'.join([f'- <@{id}> : {qty}' for id, qty in ordered_usr_stats[:10]])
    channel_detail = '\n'.join([f'- <#{id}> : {qty}' for id, qty in ordered_channel_stats[:5]])
    days = (datetime.now() - date).days

    embed = discord.Embed(
        title=f"Messages envoyés les {days} derniers jours",
        description=f'{sum(usr_stats.values())} messages envoyés.',
        color=discord.Color.blue()
    )
    if server.icon:
        embed.set_thumbnail(url=server.icon.url)
    embed.add_field(name="Les plus gros posteurs", value=user_detail, inline=False)
    embed.add_field(name="Les canaux les plus actifs", value=channel_detail, inline=False)
    return embed


@orm.db_session # type: ignore
def user_stats(server: discord.Guild, user: discord.Member) -> discord.Embed:
    date_stats: dict[str, int] = {}
    chan_stats: dict[str, int] = {}

    query = Message.select(lambda message: (
        message.server_id == server.id and
        message.user_id == user.id and
        message.channel_id != '433665712247144463'
    ))
    for message in query:
        if message.datetime > datetime.now() - timedelta(days=7):
            chan_stats[message.channel_id] = chan_stats.get(message.channel_id, 0) + 1
        date = message.datetime.strftime('%W-%Y')
        date_stats[date] = date_stats.get(date, 0) + 1

    ordered_chan_stats = sorted(chan_stats.items(), key=lambda v: v[1], reverse=True)[:5]
    ordered_date_stats = [(date.split('-')[0], qty) for date, qty in list(date_stats.items())[:-6:-1]]
    channel_detail = '\n'.join([f'- <#{id}> : {qty}' for id, qty in ordered_chan_stats])
    date_detail = '\n'.join([f' - Semaine {id} : {qty}' for id, qty in ordered_date_stats])

    embed = discord.Embed(
        title=f'Historique de @{user.display_name} sur les 7 derniers jours',
        description=f'{sum(chan_stats.values())} messages envoyés.',
        color=discord.Color.blue()
    )
    if user.avatar:
        embed.set_thumbnail(url=user.avatar.url)
    embed.add_field(name="Canaux favoris", value=channel_detail, inline=False)
    embed.add_field(name="Historique des dernières semaines", value=date_detail, inline=False)
    return embed


@orm.db_session # type: ignore
def channel_stats(
    server: discord.Guild,
    channel: discord.TextChannel | discord.VoiceChannel | discord.ForumChannel
) -> discord.Embed:
    date_stats: dict[str, int] = {}
    usr_stats: dict[str, int] = {}

    query = Message.select(lambda m: m.server_id == server.id and m.channel_id == channel.id)
    for message in query:
        if message.datetime > datetime.now() - timedelta(days=7):
            usr_stats[message.user_id] = usr_stats.get(message.user_id, 0) + 1
        date = message.datetime.strftime('%W-%Y')
        date_stats[date] = date_stats.get(date, 0) + 1

    ordered_usr_stats = sorted(usr_stats.items(), key=lambda v: v[1], reverse=True)[:10]
    ordered_date_stats = [(date.split('-')[0], qty) for date, qty in list(date_stats.items())[:-6:-1]]
    user_detail = '\n'.join([f'- <@{id}> : {qty}' for id, qty in ordered_usr_stats])
    date_detail = '\n'.join([f' - Semaine {id} : {qty}' for id, qty in ordered_date_stats])

    embed = discord.Embed(
        title=f'Historique de #{channel.name} sur les 7 derniers jours',
        description=f'{sum(usr_stats.values())} messages envoyés.',
        color=discord.Color.blue()
    )
    if server.icon:
        embed.set_thumbnail(url=server.icon.url)
    embed.add_field(name="Les plus gros posteurs", value=user_detail, inline=False)
    embed.add_field(name="Historique des dernières semaines", value=date_detail, inline=False)
    return embed


async def setup(bot: 'ThisIsTheBot') -> None:
    await bot.add_cog(Commands(bot))
    logging.info('Loaded module %s.', MODULE_NAME)
