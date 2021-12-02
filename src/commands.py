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
    
    @commands.command()
    async def register(self, ctx):
        try:
            image_url = ctx.message.attachments[0].url
        except IndexError:
            try:
                image_url = re.findall(r'https://.*?\.(?:png)|(?:jpg)|(?:webm)|(?:gif)', ctx.message.content)[0]
            except IndexError:
                await logged_send(ctx, 'There is no image in your message.')
        channel = self.bot.get_channel(916071520554614785)
        try:
            await [message for message in await channel.history().flatten() if ctx.message.author.mention in message.content][0].delete()
            erased = True
        except IndexError:
            erased = False
        message = await channel.send(f'PP de noel de {ctx.author.mention} :\n{image_url}')
        content = f'Participation validée au concours, disponible ici : <{message.jump_url}>.'
        if erased:
            content += '\nCelle-ci a remplacée ta participation précédente.'
        ctx = await logged_send(ctx, content)
    
    @commands.command()
    async def votes(self, ctx):
        channel = self.bot.get_channel(916071520554614785)
        users = []
        for message in await channel.history().flatten():
            name = ctx.guild.get_member(int(re.search(r'<@(\d+?)>', message.content).group(1))).name
            count = next(iter(reaction.count for reaction in message.reactions if reaction.custom_emoji and reaction.emoji.name == 'this'), 0)
            users.append({'name': name, 'count': count})
        content = 'Liste des participants et votants :\n'
        for user in sorted(users, key=lambda user: user['count']):
            content += f'- {user["name"]} : {user["count"]}'
        await logged_send(ctx, content)

