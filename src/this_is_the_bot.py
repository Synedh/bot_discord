import logging
from typing import Any
from discord import Message

from discord.ext import commands


class ThisIsTheBot(commands.Bot):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    async def process_commands(self, message: Message, /) -> None:
        self._log_input(message)
        await super().process_commands(message)

    async def send(self, ctx: commands.Context['ThisIsTheBot'], content: str, *args: Any) -> None:
        await ctx.send(content, *args)
        self._log_output(ctx, content)

    def _log_input(self, message: Message) -> None:
        logging.info(
            '<<< %d;%d;%d;%s',
            message.guild.id if message.guild else None,
            message.channel.id if message.channel else None,
            message.author.id if message.author else None,
            message.content
        )

    def _log_output(self, ctx: commands.Context['ThisIsTheBot'], content: str) -> None:
        logging.info(
            '>>> %d;%d;%d;%s',
            ctx.guild.id if ctx.guild else None,
            ctx.channel.id if ctx.channel else None,
            ctx.author.id if ctx.author else None,
            content
        )
