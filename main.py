import discord
import images
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from discord.ext.commands import Bot

import model

TOKEN = '<TOKEN_ID>'

client = Bot(command_prefix=("!"))
engine = create_engine('sqlite:///account.db')
session = Session(engine)
model.Base.metadata.create_all(engine)


# @client.command()
# async def quote(id, channel=None):
#     if not channel:
#         message = await client.get_message(message.channel, message_id)
#         em = discord.Embed(description=message.clean_content, colour=0xDEADBF)
#         em.set_author(name=message.author.name, icon_url=message.author.avatar_url)
#         await client.say(message.channel, embed=em)



@client.event
async def on_message(message):
    # print(message.channel.name + ' - ' + message.author.name + ' - ' + message.content)

    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    if message.content.startswith('!hello'):
        msg = 'Hello {0.author.mention}'.format(message)
        await client.send_message(message.channel, msg)

    if message.content.startswith('!save_image'):
        try:
            name = message.content.split()[1]
        except IndexError as e:
            await client.send_message(message.channel, 'No given name.')
            return
        try:
            saved = images.save_image(session, message.attachments[0]['url'], name, message.author.name)
        except IndexError as e:
            await client.send_message(message.channel, 'No given image.')
            return
        await client.send_message(message.channel, saved['msg'])

    if message.content.startswith('!image'):
        try:
            name = message.content.split()[1]
        except IndexError as e:
            await client.send_message(message.channel, 'No given name.')
            return
        resp = images.get_image(session, name)
        if resp['ok']:
            em = discord.Embed()
            em.set_image(url=resp['msg'])
            await client.send_message(message.channel, embed=em)
        else:
            await client.send_message(message.channel, resp['msg'])

    if message.content.startswith('!delete_image'):
        try:
            await client.send_message(message.channel, images.delete_image(session, message.content.split()[1])['msg'])
        except IndexError as e:
            await client.send_message(message.channel, 'No given name.')
            return

    if message.content.startswith('!list_images'):
        await client.send_message(message.channel, images.get_list(session))

    if message.content.startswith('!quote'):
        try:
            message_id = message.content.split()[1]
        except IndexError as e:
            await client.send_message(message.channel, 'No given message id.')
            return

        try:
            channel = discord.utils.find(lambda c: c.name == message.content.split()[2], message.server.channels)
            if channel is not None:
                quoted_message = await client.get_message(channel, message_id)
            else:
                await client.send_message(message.channel, 'Channel "' + channel + '" does not exist.')
        except IndexError as e:
            quoted_message = await client.get_message(message.channel, message_id)

        em = discord.Embed(description=quoted_message.clean_content, colour=quoted_message.author.roles[-1].color)
        em.set_author(name=quoted_message.author.name, icon_url=quoted_message.author.avatar_url)
        await client.send_message(message.channel, quoted_message.author.mention, embed=em)



@client.event
async def on_ready():
    print('Logged in as ' + client.user.name + ' with id : ' + str(client.user.id))
    print('------')

client.run(TOKEN)
