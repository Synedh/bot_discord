import time

def pprint(content):
    print(f'[{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}] {content}')


def log_in(ctx):
    pprint(f'<<< {ctx.guild.id};{ctx.channel.id};{ctx.author.id};{ctx.message.content}')


def log_out(ctx):
    pprint(f'>>> {ctx.guild.id};{ctx.channel.id};{ctx.author.id};{ctx.message.content}')
