import logging
from typing import Any

import discord
from discord.ext import commands

from src.errors import ForbiddenOperation, GuildOperation, ParameterError
from src.modules.stats import stats

class ThisIsTheBot(commands.Bot):
    def __init__(
        self,
        modules: list[str],
        default_server: str,
        default_channel: str,
        *args: Any,
        **kwargs: Any
    ) -> None:
        self.modules = modules
        self.default_server = default_server
        self.default_channel = default_channel
        super().__init__(*args, **kwargs)

    async def setup_hook(self) -> None:
        for module in self.modules:
            await self.load_extension(module)
        # await self.tree.sync()

    async def send(
        self,
        ctx: commands.Context['ThisIsTheBot'] | None = None,
        content: str | None = None,
        *,
        title: str | None = None,
        color: int | discord.Color = discord.Color.blue(),
        **kwargs: Any
    ) -> None:
        """
        Default function to send any message.
        Bot messages are sent as embed.
        Send a message to the default channel if ctx is null.
        """
        embed = kwargs.get('embed', discord.Embed(
            title=title,
            description=content,
            color=color
        ))
        if ctx:
            await ctx.send(**{**kwargs, 'embed': embed})
            _log_output(ctx, content, **kwargs)
        else:
            channel = self.get_channel(self.default_channel)
            await channel.send(embed=embed)
            _log_output(content, guild_id=channel.guild.id, channel_id=channel.id, **kwargs)

    async def send_error(
        self,
        ctx: commands.Context['ThisIsTheBot'],
        content: str,
        *,
        title: str = 'Error'
    ) -> None:
        """
        Default function to send error message.
        As much as possible, use bot errors from src.errors to handle exceptions.
        """
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

    @commands.Cog.listener()
    async def on_thread_create(self, thread: discord.Thread) -> None:
        await thread.join()


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
    ctx: commands.Context['ThisIsTheBot'] | None = None,
    content: str | None = None,
    *,
    embed: discord.Embed | None = None,
    guild_id: int | None = None,
    channel_id: int | None = None,
    author_id: int | None = None
) -> None:
    guild_id = guild_id if guild_id else ctx.guild.id if ctx and ctx.guild else ''
    channel_id = channel_id if channel_id else ctx.channel.id if ctx and ctx.channel else ''
    author_id = author_id if author_id else ctx.author.id if ctx and ctx.author else ''
    logging.info(
        '>>> %s;%s;%s;%s;%s',
        guild_id,
        channel_id,
        author_id,
        content if content else '',
        embed.title if embed else ''
    )
