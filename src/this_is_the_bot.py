import logging
from typing import Any

import discord
from discord.ext import commands

from src.modules.stats import stats


class ThisIsTheBot(commands.Bot):
    def __init__(self, modules: list[str], *args: Any, **kwargs: Any) -> None:
        self.modules = modules
        super().__init__(*args, **kwargs)

    async def setup_hook(self) -> None:
        for module in self.modules:
            await self.load_extension(module)
        await self.tree.sync()

    async def send(
        self,
        ctx: commands.Context['ThisIsTheBot'],
        content: str | None = None,
        **kwargs: Any
    ) -> None:
        await ctx.send(content, **kwargs)
        self._log_output(ctx, content, **kwargs)

    async def send_error(
        self,
        ctx: commands.Context['ThisIsTheBot'],
        content: str,
        *,
        title: str = 'Error',
        **kwargs: Any
    ) -> None:
        embed = discord.Embed(
            title=title,
            description=content,
            color=discord.Color.red()
        )
        await ctx.send(embed=embed, ephemeral=True, **kwargs)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message, /) -> None:
        if not message.author.bot:
            self._log_message(message)
            stats.add_entry(message)
        await super().on_message(message)

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction['ThisIsTheBot']) -> None:
        if interaction.data and interaction.type == discord.InteractionType.application_command:
            self._log_input(interaction)

    @commands.Cog.listener()
    async def on_command_error(
        self,
        ctx: commands.Context['ThisIsTheBot'], # type: ignore
        error: commands.CommandError,
        /
    ) -> None:
        logging.error(
            'Ignoring exception in command %s:',
            ctx.command,
            exc_info=(type(error), error, error.__traceback__)
        )
        await self.send_error(ctx, f'Exception occured in command :\n{error}')
        await super().on_command_error(ctx, error)

    def _log_message(self, message: discord.Message) -> None:
        logging.info(
            '--- %d;%d;%d;%s',
            message.guild.id if message.guild else None,
            message.channel.id if message.channel else None,
            message.author.id if message.author else None,
            message.content
        )

    def _log_input(self, interaction: discord.Interaction['ThisIsTheBot']) -> None:
        logging.info(
            '<<< %d;%d;%d;%s',
            interaction.guild.id if interaction.guild else None,
            interaction.channel.id if interaction.channel else None,
            interaction.user.id if interaction.user else None,
            interaction.data
        )

    def _log_output(
        self,
        ctx: commands.Context['ThisIsTheBot'],
        content: str | None = None,
        embed: discord.Embed | None = None
    ) -> None:
        logging.info(
            '>>> %d;%d;%d;%s;%s',
            ctx.guild.id if ctx.guild else None,
            ctx.channel.id if ctx.channel else None,
            ctx.author.id if ctx.author else None,
            content,
            embed.title if embed else None
        )
