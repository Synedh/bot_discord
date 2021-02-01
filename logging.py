import time

def pprint(content):
    print(f'[{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}] {content}')


def log_in(ctx):
    pprint(f'<<< Server: {ctx.guild.id} - Channel: {ctx.channel.id} - User:{ctx.author.id} - {ctx.message.content}')


def log_out(ctx):
    pprint(f'>>> Server: {ctx.guild.id} - Channel: {ctx.channel.id} - User:{ctx.author.id} - {ctx.message.content}')
