import logging

from discord.ext import commands

from src.this_is_the_bot import ThisIsTheBot

MODULE_NAME = "Default"

class DefaultCommands(commands.Cog, name=MODULE_NAME):
    def __init__(self, bot: ThisIsTheBot):
        self.bot = bot

    @commands.command()
    async def hello(self, ctx: commands.Context[ThisIsTheBot]) -> None:
        '''Send a friendly hello message'''
        await self.bot.send(ctx, f'Hello {ctx.message.author.mention} !')

async def setup(bot: ThisIsTheBot) -> None:
    await bot.add_cog(DefaultCommands(bot))
    logging.info('Loaded module %s.', MODULE_NAME)
