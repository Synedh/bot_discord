import asyncio
from datetime import datetime, timedelta

from discord.ext import tasks, commands

from .stats import week_stats
from .birthday import send_birthdays
from .logger import pprint


class CustomBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.bg_task = self.loop.create_task(self.weekly_stats())
        self.birthdays.start()
        self.first = True
        self.default_channel = kwargs['default_channel']
        self.default_server = kwargs['default_server']

    def __get_next_iteration(self):
        now = datetime.now()
        days_until_monday = (0 - now.weekday() - 1) % 7 + 1
        delta = now.replace(hour=9, minute=0, second=0) + timedelta(days=days_until_monday) - now
        return delta.total_seconds()
    
    def __log_task(self, server_id, channel_id, content):
        pprint(f'>>> {server_id};{channel_id};{self.user.id};{repr(content)}')

    async def weekly_stats(self):
        await self.wait_until_ready()
        channel = self.get_channel(self.default_channel)
        next_date = self.__get_next_iteration()
        if self.first:
            self.first = False
            pprint(f'Next weekly stats in {timedelta(seconds=next_date)}')
        else:
            stats = week_stats(self.default_server)
            self.__log_task(self.default_server, self.default_channel, stats)
            await channel.send(stats)
        await asyncio.sleep(next_date)
    
    @tasks.loop(minutes=2.0)
    async def birthdays(self):
        await self.wait_until_ready()
        channel = self.get_channel(self.default_channel)
        birthdays = send_birthdays(auto=True)
        if not birthdays:
            return
        self.__log_task(self.default_server, self.default_channel, birthdays)
        await channel.send(birthdays)
        
