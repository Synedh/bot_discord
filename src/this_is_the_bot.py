import logging
from typing import Any

import discord
from discord.ext import commands

from src.errors import ForbiddenOperation, GuildOperation, ParameterError
from src.modules.stats import stats

class ThisIsTheBot(commands.Bot):
    def __init__(self, modules: list[str], *args: Any, **kwargs: Any) -> None:
        self.modules = modules
        super().__init__(*args, **kwargs)

    async def setup_hook(self) -> None:
        for module in self.modules:
            await self.load_extension(module)
        # await self.tree.sync()

    async def send(
        self,
        ctx: commands.Context['ThisIsTheBot'],
        content: str | None = None,
        *,
        title: str | None = None,
        color: int | discord.Color = discord.Color.blue(),
        **kwargs: Any
    ) -> None:
        embed = kwargs.get('embed', discord.Embed(
            title=title,
            description=content,
            color=color
        ))
        await ctx.send(**{**kwargs, 'embed': embed})
        _log_output(ctx, content, **kwargs)

    async def send_error(
        self,
        ctx: commands.Context['ThisIsTheBot'],
        content: str,
        *,
        title: str = 'Error'
    ) -> None:
        await self.send(ctx, content, title=title, color=discord.Color.red(), ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message, /) -> None:
        if not message.author.bot:
            _log_message(message)
            stats.add_entry(message)
        await super().on_message(message)

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction['ThisIsTheBot']) -> None:
        if interaction.data and interaction.type == discord.InteractionType.application_command:
            _log_input(interaction)

    @commands.Cog.listener()
    async def on_command_error(
        self,
        ctx: commands.Context['ThisIsTheBot'], # type: ignore
        error: commands.CommandError,
        /
    ) -> None:
        if (
            error.__cause__ and
            type(error.__cause__.__cause__) in [ForbiddenOperation, GuildOperation, ParameterError]
        ):
            return await self.send_error(ctx, str(error.__cause__.__cause__))
        logging.error(
            'Ignoring exception in command %s:',
            ctx.command,
            exc_info=(type(error), error, error.__traceback__)
        )
        await self.send_error(ctx, f'Exception occured in command :\n{error}')
        await super().on_command_error(ctx, error)

def _log_message(message: discord.Message) -> None:
    logging.info(
        '--- %s;%s;%s;%s',
        message.guild.id if message.guild else '',
        message.channel.id if message.channel else '',
        message.author.id if message.author else '',
        message.content
    )

def _log_input(interaction: discord.Interaction['ThisIsTheBot']) -> None:
    logging.info(
        '<<< %s;%s;%s;%s',
        interaction.guild.id if interaction.guild else '',
        interaction.channel.id if interaction.channel else '',
        interaction.user.id if interaction.user else '',
        interaction.data
    )

def _log_output(
    ctx: commands.Context['ThisIsTheBot'],
    content: str | None = None,
    embed: discord.Embed | None = None
) -> None:
    logging.info(
        '>>> %s;%s;%s;%s;%s',
        ctx.guild.id if ctx.guild else '',
        ctx.channel.id if ctx.channel else '',
        ctx.author.id if ctx.author else '',
        content if content else '',
        embed.title if embed else ''
    )
