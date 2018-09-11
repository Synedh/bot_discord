import asyncio
from datetime import datetime

async def stats_background(bot):
    await bot.wait_until_ready()
    channel = bot.get_channel('433665712247144463')
    while not bot.is_closed:
        now = datetime.now().strftime('%d-%m-%Y %H:%M')
        if now == '10-09-2018 11:12':
            await bot.send_message(channel, 'test')
            asyncio.sleep(60)
        asyncio.sleep(1)
