import logging
from typing import Literal, TypedDict

import requests
import discord
from discord.ext import commands

from src.this_is_the_bot import ThisIsTheBot

MODULE_NAME = "NSFW"


class ApiImage(TypedDict):
    model: str | None
    preview: str
    id: int
    rank: int
    author: str | None

class NsfwCommands(commands.Cog, name=MODULE_NAME):
    def __init__(self, bot: ThisIsTheBot):
        self.bot = bot

    @commands.is_nsfw() # type: ignore
    @commands.hybrid_command()
    async def boobs(self, ctx: commands.Context[ThisIsTheBot]) -> None:
        '''NSFW - Get a random boobs image'''
        embed = self._build_embed('boobs')
        await self.bot.send(ctx, embed=embed)

    @commands.is_nsfw() # type: ignore
    @commands.hybrid_command()
    async def ass(self, ctx: commands.Context[ThisIsTheBot]) -> None:
        '''NSFW - Get a random butt image'''
        embed = self._build_embed('butts')
        await self.bot.send(ctx, embed=embed)

    def _build_embed(self, api_type: Literal['boobs'] | Literal['butts']) -> discord.Embed:
        result: ApiImage = requests.get(
            f'http://api.o{api_type}.ru/{api_type}/0/1/random',
            timeout=5000
        ).json()[0]
        return (
            discord.Embed(url=f'https://o{api_type}.ru/b/{result["id"]}/')
                   .set_image(url=f'https://media.o{api_type}.ru/{result["preview"]}')
                   .set_footer(text=f'#{result["id"]} • Rank: {result["rank"]}')
        )


async def setup(bot: ThisIsTheBot) -> None:
    await bot.add_cog(NsfwCommands(bot))
    logging.info('Loaded module %s.', MODULE_NAME)
