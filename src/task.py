from discord.ext import tasks, commands
from datetime import datetime, timedelta

class MondayList(commands.Cog):
    def __init__(self):
        self.start = True
        self.task.start()
    
    @tasks.loop(minutes=1)
    async def task(self):
        if self.start:
            self.start = False
            return 
        pass

    @task.after_loop()
    async def check_next_iteration(self):
        now = datetime.now()
        next_monday = timedelta(days=(0 - now.weekday() - 1) % 7 + 1)
        pass

    def stop(self):
        self.task.cancel()