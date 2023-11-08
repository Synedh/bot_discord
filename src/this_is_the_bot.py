import logging
from typing import Any

from discord import Interaction, InteractionType, Message
from discord.ext import commands


class ThisIsTheBot(commands.Bot):
    def __init__(self, modules: list[str], *args: Any, **kwargs: Any) -> None:
        self.modules = modules
        super().__init__(*args, **kwargs)

    async def setup_hook(self) -> None:
        for module in self.modules:
            await self.load_extension(module)
        await self.tree.sync()

    async def send(self, ctx: commands.Context['ThisIsTheBot'], content: str, *args: Any) -> None:
        await ctx.send(content, *args)
        self._log_output(ctx, content)

    @commands.Cog.listener()
    async def on_message(self, message: Message) -> None:
        if not message.author.bot:
            self._log_message(message)

    @commands.Cog.listener()
    async def on_interaction(self, interaction: Interaction['ThisIsTheBot']) -> None:
        if interaction.data and interaction.type == InteractionType.application_command:
            self._log_input(interaction)

    def _log_message(self, message: Message) -> None:
        logging.info(
            '--- %d;%d;%d;%s',
            message.guild.id if message.guild else None,
            message.channel.id if message.channel else None,
            message.author.id if message.author else None,
            message.content
        )

    def _log_input(self, interaction: Interaction['ThisIsTheBot']) -> None:
        logging.info(
            '<<< %d;%d;%d;%s',
            interaction.guild.id if interaction.guild else None,
            interaction.channel.id if interaction.channel else None,
            interaction.user.id if interaction.user else None,
            interaction.data
        )

    def _log_output(self, ctx: commands.Context['ThisIsTheBot'], content: str) -> None:
        logging.info(
            '>>> %d;%d;%d;%s',
            ctx.guild.id if ctx.guild else None,
            ctx.channel.id if ctx.channel else None,
            ctx.author.id if ctx.author else None,
            content
        )
