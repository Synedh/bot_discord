import random
import discord
from discord.ext.commands import Bot
from discord.errors import HTTPException, NotFound
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

import images
import model

token = None
with open('token') as file:
    token = file.readline()[:-1].split('=')[1]

bot = Bot(command_prefix=("!"))
engine = create_engine('sqlite:///account.db')
session = Session(engine)
model.Base.metadata.create_all(engine)

command_list = [
    'hello',
    'save_image',
    'image',
    'delete_image',
    'list_images',
    'quote',
    'roll',
    'pick'
]


@bot.command(pass_context=True)
async def hello(ctx):
    bot.say('Hello ' + ctx.message.author.mention + ' !')


@bot.command(pass_context=True)
async def save_image(ctx, img_name=None):
    if img_name == None:
        await bot.say('No given name.')
    else:
        try:
            saved = images.save_image(session, ctx.message.attachments[0]['url'], img_name, ctx.message.author.display_name)
            await bot.say(saved['msg'])
        except IndexError as e:
            await bot.say('No given image.')


@bot.command(pass_context=True)
async def image(ctx, img_name=None):
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
    if img_name == None:
        await bot.say('No given name.')
    else:
        await bot.say(images.delete_image(session, img_name)['msg'])


@bot.command(pass_context=True)
async def list_images(ctx):
    await bot.say('Deprecated command, go to https://c.ddns.net instead.')
    # msgs = images.get_list(session)
    # for msg in msgs:
    #     await bot.send_message(ctx.message.author, '```' + msg + '```')
    # await bot.say('Sent list in private message.')


@bot.command(pass_context=True)
async def quote(ctx, msg_id=None, channel=None):
    if not msg_id:
        await bot.say('No given message id.')
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
async def roll(arg1=None, arg2=None):
    try:
        if arg1 == None:
            await bot.say('Nothing to roll !')
        elif arg2 == None:
            await bot.say('Rolled ' + str(random.randint(1, int(arg1))) + '.')
        elif int(arg1) < 2000:
            values = [random.randint(1, int(arg2)) for i in range(0, int(arg1))]
            await bot.say('Rolled ' + ', '.join([str(value) for value in values]) + '.\nTotal value : ' + str(sum(values)) + '.')
        else:
            await bot.say('Too many dices to roll !')
    except ValueError as e:
        await bot.say('Invalid dice values.')
    except HTTPException as e:
        await bot.say('Too many dices to roll !')


@bot.command()
async def pick(*choices: str):
    if len(choices) > 0:
        await bot.say('Picked ' + random.choice(choices) + '.')
    else:
        await bot.say('No value to pick !')


@bot.event
async def on_message(message):
    # print('{0} - {1} - {2} - {3}'.format(message.server, message.channel, message.author, message.content))
    if len(message.content) > 0 and message.content.split()[0][1:] in command_list:
        await bot.process_commands(message)

@bot.event
async def on_ready():
    print('Logged in as ' + bot.user.name + ' with id : ' + str(bot.user.id))
    print('------')

bot.run(token)
