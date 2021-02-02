from discord.ext import tasks, commands
from datetime import datetime, timedelta

class MondayList(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start = True
        self.test.start()
    
    @tasks.loop(seconds=5, count=1)
    async def test(self):
        if self.start:
            self.start = False
            return
        print('task')

    @test.after_loop
    async def check_next_iteration(self):
        now = datetime.now()
        days_until_monday = (0 - now.weekday() - 1) % 7 + 1
        sec_until_next = (now.replace(day=now.day + days_until_monday, hour=9, minute=30, second=0) - now).total_seconds()
        print(sec_until_next)
        self.test.change_interval(seconds=sec_until_next)
        self.test.cancel()
        self.test.start()

    def stop(self):
        print('Stoping task')
        self.test.cancel()
    
    @commands.command()
    async def next_report(self, ctx):
        """ Show next monday report """
        print(self.test.next_iteration)
        await ctx.send(self.test.next_iteration)