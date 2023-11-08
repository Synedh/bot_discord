import logging
import random
import re

import requests
from discord.ext import commands

from src.this_is_the_bot import ThisIsTheBot

MODULE_NAME = "Default"


class DefaultCommands(commands.Cog, name=MODULE_NAME):
    def __init__(self, bot: ThisIsTheBot):
        self.bot = bot

    @commands.hybrid_command() #type: ignore
    async def hello(self, ctx: commands.Context[ThisIsTheBot]) -> None:
        '''Send a friendly hello message'''
        await self.bot.send(ctx, f'Hello {ctx.message.author.mention} !')

    @commands.hybrid_command() # type: ignore
    async def pick(self, ctx: commands.Context[ThisIsTheBot], choices: str) -> None:
        """Sometimes important choices depend on a simple bot."""
        choice_list = re.findall(r'(?:[^\s,"]|"(?:\\.|[^"])*")+', choices)
        if len(choice_list) > 0:
            await self.bot.send(ctx, f'Picked "{random.choice(choice_list)}".')
        else:
            await self.bot.send(ctx, 'No value to pick !')


    @commands.hybrid_command() # type: ignore
    async def roll(self, ctx: commands.Context[ThisIsTheBot], dice: commands.Range[int, 1, 100], qty: commands.Range[int, 1, 100] | None=None) -> None:
        """Roll some dices."""
        try:
            if qty is None:
                await self.bot.send(ctx, 'Nothing to roll !')
            elif dice is None:
                await self.bot.send(ctx, f'Rolled {random.randint(1, qty)}.')
            elif int(qty) < 2000:
                values = [random.randint(1, dice) for _ in range(qty)]
                values_str = ', '.join(map(str, values))
                await self.bot.send(ctx, f'Rolled {values_str}.\nTotal value : {sum(values)}.')
            else:
                await self.bot.send(ctx, 'Too many dices to roll !')
        except ValueError:
            await self.bot.send(ctx, 'Invalid dice values.')


    @commands.hybrid_command() # type: ignore
    async def yt(self, ctx: commands.Context[ThisIsTheBot], keywords: str) -> None:
        """Send first result of youtube research with given keywords."""
        keyword_list = keywords.split()
        if keyword_list:
            query = "+".join(keyword_list)
            results = requests.get(f'https://www.youtube.com/results?search_query={query}').text
            try:
                video_path = re.search(r'\"(\/watch\?v=.*?)\"', results)[1] # type: ignore
                await self.bot.send(ctx, f'https://youtube.com{video_path}')
            except IndexError:
                await self.bot.send(ctx, 'No video found.')
        else:
            await self.bot.send(ctx, 'No keyword to search')


    # @commands.command()
    # async def poll(self, ctx: commands.Context[ThisIsTheBot], question: str | None=None, *answers: str) -> None:
    #     """Create a new poll with given question and answers."""
    #     emotes = ['1⃣', '2⃣', '3⃣', '4⃣', '5⃣', '6⃣', '7⃣', '8⃣', '9⃣', '🔟']
    #     if not question:
    #         await self.bot.send(ctx, 'I need a least a question and two answers to start a poll !')
    #     elif len(answers) < 2:
    #         await self.bot.send(ctx, 'I need at least two answers to start a poll !')
    #     elif len(answers) > 10:
    #         await self.bot.send(ctx, 'I can\'t start a poll with that much options !')
    #     else:
    #         questions = '\n'.join(f'{emotes[i]} {answer}' for i, answer in enumerate(answers))
    #         message = await self.bot.send(ctx, f'**Nouveau sondage !\n{question}\n{questions}**\n')
    #         for i in range(len(answers)):
    #             await message.add_reaction(emotes[i])

async def setup(bot: ThisIsTheBot) -> None:
    await bot.add_cog(DefaultCommands(bot))
    logging.info('Loaded module %s.', MODULE_NAME)
