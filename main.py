import discord
import images
from discord.ext.commands import Bot

TOKEN = 'MzM5Mzg5NTE4NjQzNzI0Mjkx.Da_IbQ.ZzBwGKSehVd8TrCIsoqGFf45xBQ'

client = Bot(command_prefix=("!"))


# @client.command()
# async def quote(id, channel=None):
#     if not channel:
#         message = await client.get_message(message.channel, message_id)
#         em = discord.Embed(description=message.clean_content, colour=0xDEADBF)
#         em.set_author(name=message.author.name, icon_url=message.author.avatar_url)
#         await client.say(message.channel, embed=em)



@client.event
async def on_message(message):
    print(message.channel.name + ' - ' + message.author.name + ' - ' + message.content)

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
            saved = images.save_image(message.attachments[0]['url'], name)
        except IndexError as e:
            await client.send_message(message.channel, 'No given image.')
            return
        if saved:
            await client.send_message(message.channel, 'Image saved as "' + name + '".')
        else:
            await client.send_message(message.channel, 'Unknown error.')

    if message.content.startswith('!image'):
        try:
            name = message.content.split()[1]
        except IndexError as e:
            await client.send_message(message.channel, 'No given name.')
            return
        image = images.get_image(name)
        await client.send_file(message.channel, image)

    if message.content.startswith('!quote'):
        try:
            message_id = message.content.split()[1]
        except IndexError as e:
            await client.send_message(message.channel, 'No given message id.')
            return
        try:
            message = await client.get_message(message.content.split()[2], message_id)
        except IndexError as e:
            message = await client.get_message(message.channel, message_id)
        message = await client.get_message(message.channel, message_id)
        em = discord.Embed(description=message.clean_content, colour=0xDEADBF)
        em.set_author(name=message.author.name, icon_url=message.author.avatar_url)
        await client.send_message(message.channel, embed=em)



@client.event
async def on_ready():
    print('Logged in as ' + client.user.name + ' with id : ' + str(client.user.id))
    print('------')

client.run(TOKEN)
