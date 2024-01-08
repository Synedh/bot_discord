# ThiS is ThE BoT

Discord bot written in Python 3.11 using [discord.py](https://discordpy.readthedocs.io/) library.

### Developer usage
- Clone repository
- Create and activate virtual environment
- Install dependencies from `requirements.txt` file.
- Fill `.env` file based on given example.
- Use `./main.py` to launch bot.

### Propose a module
This bot is using [Cog](https://discordpy.readthedocs.io/en/stable/ext/commands/cogs.html) functionality to power independent modules. Each module is based on the following code and sorted in the `src/modules/` folder:
```
import logging

from discord.ext import commands

from src.this_is_the_bot import ThisIsTheBot

MODULE_NAME = "foo"

class Commands(commands.Cog, name=MODULE_NAME):
    def __init__(self, bot: ThisIsTheBot):
        self.bot = bot

    @commands.hybrid_command() #type: ignore
    async def bar(self, ctx: commands.Context[ThisIsTheBot]) -> None:
        '''Command description'''
        await self.bot.send(ctx, 'content')

async def setup(bot: ThisIsTheBot) -> None:
    await bot.add_cog(Commands(bot))
    logging.info('Loaded module %s.', MODULE_NAME)

```

For an advanced module with several files, just put your files in a folder with a `__init__.py` file importing your setup function.
