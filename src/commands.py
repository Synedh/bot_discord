import re
import random

import requests
from pony import orm
from discord.ext import commands

from .logger import logged_send


class DefaultCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
 
    @commands.command() 
    async def hello(self, ctx):
        '''Send a friendly hello message'''
        await logged_send(ctx, f'Hello {ctx.message.author.mention} !')

    @commands.command()
    async def pick(self, ctx, *choices: str):
        """Sometimes important choices depend on a simple bot."""
        if len(choices) > 0:
            await logged_send(ctx, f'Picked "{random.choice(choices)}".')
        else:
            await logged_send(ctx, 'No value to pick !')


    @commands.command()
    async def roll(self, ctx, qty: int=None, dice: int=None):
        """Roll some dices."""
        try:
            if qty is None:
                await logged_send(ctx, 'Nothing to roll !')
            elif dice is None:
                await logged_send(ctx, f'Rolled {random.randint(1, qty)}.')
            elif int(qty) < 2000:
                values = [random.randint(1, dice) for i in range(qty)]
                await logged_send(ctx, f'Rolled {", ".join([str(value) for value in values])}.\nTotal value : {sum(values)}.')
            else:
                await logged_send(ctx, 'Too many dices to roll !')
        except ValueError:
            await logged_send(ctx, 'Invalid dice values.')


    @commands.command()
    async def yt(self, ctx, *keywords: str):
        """Send first result of youtube research with given keywords."""
        if len(keywords) > 0:
            results = requests.get(f'https://www.youtube.com/results?search_query={"+".join(keywords)}').text
            video_path = re.search(r'\"(\/watch\?v=.*?)\"', results)[1]
            await logged_send(ctx, f'https://youtube.com{video_path}')
        else:
            await logged_send(ctx, 'No keyword to search')


    @commands.command()
    async def poll(self, ctx, question: str=None, *answers: str):
        """Create a new poll with given question and answers."""
        emotes = ['1⃣', '2⃣', '3⃣', '4⃣', '5⃣', '6⃣', '7⃣', '8⃣', '9⃣', '🔟']
        if not question:
            await logged_send(ctx, 'I need a least a question and two answers to start a poll !')
        elif len(answers) < 2:
            await logged_send(ctx, 'I need at least two answers to start a poll !')
        elif len(answers) > 10:
            await logged_send(ctx, 'I can\'t start a poll with that much options !')
        else:
            message = await logged_send(ctx, '**Nouveau sondage !\n%s**\n' % question + '\n'.join(['%s %s' % (emotes[i], answer) for i, answer in enumerate(answers)]))
            for i in range(len(answers)):
                await message.add_reaction(emotes[i])
