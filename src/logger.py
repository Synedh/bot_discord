import time

def pprint(content):
    print(f'[{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}] {content}')


def log_in(message):
    try:
        pprint(f'<<< {message.guild.id};{message.channel.id};{message.author.id};{repr(message.content)}')
    except ValueError:
        pprint(f'<<< {message.guild.id};{message.channel.id};{message.author.id};<no_string_content>')


def log_out(ctx, content):
    pprint(f'>>> {ctx.guild.id};{ctx.channel.id};{ctx.bot.user.id};{repr(content)}')


async def logged_send(ctx, content):
    log_out(ctx, content)
    return await ctx.send(content)
