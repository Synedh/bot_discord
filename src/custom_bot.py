import asyncio
from datetime import datetime, timedelta

from discord.ext import commands

from .stats import week_stats
from .logger import pprint


class CustomBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.bg_task = self.loop.create_task(self.weekly_stats())
        self.first = True

    def __get_next_iteration__(self):
        now = datetime.now()
        days_until_monday = (0 - now.weekday() - 1) % 7 + 1
        delta = now.replace(day=now.day + days_until_monday, hour=9, minute=0, second=0) - now
        return delta.total_seconds()
    
    def __log_task__(self, server_id, channel_id, content):
        pprint(f'>>> {server_id};{channel_id};{self.user.id};{repr(content)}')

    async def weekly_stats(self):
        await self.wait_until_ready()
        channel = self.get_channel(433665712247144463)
        while not self.is_closed():
            next_date = self.__get_next_iteration__()
            if self.first:
                self.first = False
                pprint(f'Next weekly stats in {timedelta(seconds=next_date)}')
            else:
                stats = week_stats(202909295526805505)
                self.__log_task__(202909295526805505, 433665712247144463, stats)
                await channel.send(stats)
            await asyncio.sleep(next_date)
