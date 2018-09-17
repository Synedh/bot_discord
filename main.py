import os
import re
import random
import discord
import requests
from discord.ext.commands import Bot
from discord.errors import HTTPException, NotFound
from discord.ext.commands.errors import CommandNotFound
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from datetime import datetime

import model
from bot import images
from bot import stats as stats_command
from bot.hangman import Hangman
from bot.moreorless import MoreOrLess
# from bot.background_tasks import stats_background

token = None
with open('token') as file:
    token = file.readline()[:-1].split('=')[1]

bot = Bot(command_prefix=("!"))
engine = create_engine('sqlite:///account.db')
session = Session(engine)
model.Base.metadata.create_all(engine)

dir_path = os.path.dirname(os.path.realpath(__file__))
command_list = [
    'hello',
    'help',
    'save_image',
    'image',
    'delete_image',
    'list_images',
    'more_or_less',
    'pendu',
    'quote',
    'roll',
    'pick',
    'stats',
    'yt'
]
mol = None
mh = None


@bot.command(pass_context=True)
async def hello(ctx):
    """Answer Hello to command sender."""
    await bot.say('Hello ' + ctx.message.author.mention + ' !')


@bot.command(pass_context=True)
async def save_image(ctx, img_name=None):
    """Save an image in bot database."""
    if img_name == None:
        await bot.say('No given name.')
    else:
        try:
            saved = images.save_image(session, ctx.message.attachments[0]['url'], img_name, str(ctx.message.author))
            await bot.say(saved['msg'])
        except IndexError as e:
            await bot.say('No given image.')


@bot.command(pass_context=True)
async def image(ctx, img_name=None):
    """Print image of given name."""
    if img_name == None:
        await bot.say('No given name.')
    else:
        resp = images.get_image(session, img_name)
        if resp['ok']:
            em = discord.Embed()
            em.set_image(url=resp['msg'])
            await bot.send_message(ctx.message.channel, embed=em)
        else:
            await bot.say(resp['msg'])


@bot.command()
async def delete_image(img_name=None):
    """Delete image of given name."""
    if img_name == None:
        await bot.say('No given name.')
    else:
        await bot.say(images.delete_image(session, img_name)['msg'])


@bot.command(pass_context=True)
async def list_images(ctx):
    """Deprecated command, go to https://tite.synedh.fr instead."""
    await bot.say('Deprecated command, go to https://tite.synedh.fr instead.')


@bot.command(pass_context=True)
async def quote(ctx, msg_id=None, channel=None):
    """Quote message of given id. Specify channel if not current."""
    if not msg_id:
        await bot.say('No given message id.')
        return
    elif channel:
        quote_channel = discord.utils.find(lambda c: c.name == channel, ctx.message.server.channels)
        if not quote_channel:
            await bot.say('Channel `' + channel + '` does not exists.')
            return
    else:
        quote_channel = ctx.message.channel
    try:
        msg = await bot.get_message(quote_channel, msg_id)
    except (HTTPException, NotFound):
        await bot.say('Message with id `' + msg_id + '` does not exists.')
        return
    em = discord.Embed(description=msg.clean_content, colour=msg.author.roles[-1].color)
    em.set_author(name=msg.author.name, icon_url=msg.author.avatar_url)
    await bot.say(msg.author.mention, embed=em)


@bot.command()
async def roll(qty=None, dice=None):
    """Roll some dices."""
    try:
        if qty == None:
            await bot.say('Nothing to roll !')
        elif dice == None:
            await bot.say('Rolled ' + str(random.randint(1, int(qty))) + '.')
        elif int(qty) < 2000:
            values = [random.randint(1, int(dice)) for i in range(0, int(qty))]
            await bot.say('Rolled ' + ', '.join([str(value) for value in values]) + '.\nTotal value : ' + str(sum(values)) + '.')
        else:
            await bot.say('Too many dices to roll !')
    except ValueError as e:
        await bot.say('Invalid dice values.')
    except HTTPException as e:
        await bot.say('Too many dices to roll !')


@bot.command()
async def pick(*choices: str):
    """Sometimes important choices depend on a simple bot."""
    if len(choices) > 0:
        await bot.say('Picked ' + random.choice(choices) + '.')
    else:
        await bot.say('No value to pick !')


@bot.command()
async def yt(*keywords: str):
    """Send first result of youtube research with given keywords."""
    if len(keywords) > 0:
        await bot.say((
            'https://youtube.com%s' 
            % (re.search(r'href=\"(/watch\?v=.*?)\"',
            requests.get('https://www.youtube.com/results?search_query=%s' % '+'.join(keywords)).text)[1])
        ))
    else:
        await bot.say('No keyword to search')


@bot.command()
async def more_or_less(command: str):
    """Start a new More or Less game with !more_or_less start"""
    global mol
    if command == 'start':
        mol = MoreOrLess()
        await bot.say('Started new More or Less game.')
        await bot.say(mol.message1())
    elif mol and command == 'stop':
        await bot.say(mol.message3())
        mol = None
    else:
        try:
            status, message = mol.entry(int(command))
            await bot.say(message)
            if status == 1:
                await bot.say(mol.message1())
            elif status == 2:
                await bot.say(mol.message2())
            elif status == 3:
                await bot.say(mol.message3())
                mol = None
        except ValueError as e:
            await bot.say('Invalid given value %s : must be an integer.' % command)
        except AttributeError as e:
            await bot.say('Not any game started. Type "!more_or_less start" to start new game.'
)

@bot.command()
async def pendu(command: str):
    """Start a new hangman with !pendu start (fr only)."""
    global hm
    if command == 'start':
        hm = Hangman()
        await bot.say('Démarré nouveau pendu.')
        await bot.say(hm.print_stats())
        await bot.say(hm.turn_message)
    elif hm and command == 'stop':
        await bot.say(hm.close_message)
        hm = None
    elif hm:
        status, message = hm.try_value(command.upper())
        await bot.say(message)
        if status == 0:
            await bot.say(hm.turn_message)
        elif status == 1:
            await bot.say(hm.print_stats())
            await bot.say(hm.turn_message)
        elif status == 2:
            await bot.say(hm.print_stats())
            await bot.say(hm.defeat_message)
            await bot.say(hm.solution_message)
            await bot.say(hm.close_message)
            hm = None
        elif status == 3:
            await bot.say(hm.print_stats())
            await bot.say(hm.victory_message)
            await bot.say(hm.close_message)
            hm = None
    else:
        await bot.say('Invalid given value %s : do you want to start a new game ?' % command)

@bot.command(pass_context=True)
async def stats(ctx, detail: str=''):
    """Get stats of given server. Use @user or #channel for details."""
    if detail == '':
        await bot.say(stats_command.week_stats(session, ctx.message.server))
    elif detail[1] == '@':
        await bot.say(stats_command.user_stats(session, ctx.message.server, detail))
    elif detail[1] == '#':
        await bot.say(stats_command.channel_stats(session, ctx.message.server, detail))
    else:
        await bot.say('Invalid given value %s. Please tag a channel or a user.' % detail)


@bot.event
async def on_message(message):      
    stats_command.add_entry(session, message)
    if len(message.content) > 0 and message.content.split()[0][1:] in command_list:
        with open(dir_path + '/log/commands.log', "a+") as file:
            file.write(
                '{0};{1};{2};{3};{4}\n'.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                message.server, message.channel, message.author, message.content)
            )
        await bot.process_commands(message)


@bot.event
async def on_ready():
    print('Logged in as ' + bot.user.name + ' with id : ' + str(bot.user.id))
    print('------')

# bot.loop.create_task(stats_background(bot))
bot.run(token)
