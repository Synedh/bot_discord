#!/usr/bin/env python

import logging

from src.settings import TOKEN, bot

@bot.event
async def on_ready() -> None:
    logging.info('Logged in as %s.', bot.user)

bot.run(TOKEN)
