#!/usr/bin/env python

import logging

import discord
from discord.ext import commands

from src.settings import (DEFAULT_CHANNEL, DEFAULT_SERVER, PREFIX, TOKEN,
                          database, modules)
from src.this_is_the_bot import ThisIsTheBot

bot = ThisIsTheBot(
    modules=modules,
    command_prefix=commands.when_mentioned_or(PREFIX),
    intents=discord.Intents.all(),
    pm_help=True,
    default_channel=DEFAULT_CHANNEL,
    default_server=DEFAULT_SERVER,
)

@bot.event
async def on_ready() -> None:
    logging.info('Logged in as %s.', bot.user)
    database.generate_mapping(create_tables=True)

bot.run(TOKEN)
