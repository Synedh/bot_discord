import requests
from pony import orm
from pony.orm.core import ObjectNotFound
from discord.ext import commands

from .models import NSFWChannel
from .logger import logged_send

class NSFWCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def nsfw(self, ctx, command: str):
        '''Allow nsfw commands for current channel'''
        if command == 'allow':
            chan = add_chan(ctx.channel.id)
            await logged_send(ctx, f'Allowed NSFW posts on chan <#{chan.id}>.')
        elif command == 'deny':
            rm_chan(ctx.channel.id)
            await logged_send(ctx, f'Removed chan <#{ctx.channel.id}> for allowed NSFW chans.')
        elif command == 'list':
            chans = '\n'.join(f'- <#{chan.id}>' for chan in get_chans())
            await logged_send(ctx, f'Liste des chans autorisés en NSFW :\n{chans}')
        else:
            await logged_send(ctx, f'Unknown argument {command}.')
    
    @commands.command()
    async def boobs(self, ctx):
        '''NSFW - Get a random boobs image'''
        try:
            get_chan(ctx.channel.id)
            response = requests.get('http://api.oboobs.ru/boobs/0/1/random').json()
            await logged_send(ctx, f'http://media.oboobs.ru/{response[0]["preview"]}')
        except ObjectNotFound:
            await logged_send(ctx, f'NSFW posts are not allowed in this chan.')
    
    @commands.command()
    async def ass(self, ctx):
        '''NSFW - Get a random butt image'''
        try:
            get_chan(ctx.channel.id)
            response = requests.get('http://api.obutts.ru/butts/0/1/random').json()
            await logged_send(ctx, f'http://media.obutts.ru/{response[0]["preview"]}')
        except ObjectNotFound:
            await logged_send(ctx, f'NSFW posts are not allowed in this chan.')


@orm.db_session
def get_chans():
    return list(NSFWChannel.select())


@orm.db_session
def get_chan(chan_id):
    return NSFWChannel[str(chan_id)]


@orm.db_session
def add_chan(chan_id):
    chan = NSFWChannel(id=str(chan_id))
    orm.commit()
    return chan


@orm.db_session
def rm_chan(chan_id):
    NSFWChannel.select(lambda chan: chan.id == str(chan_id)).first().delete()
