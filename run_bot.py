import asyncio
from datetime import datetime

from kts_backend.store.bot.base import Bot


def run_bot():
    loop = asyncio.get_event_loop()
    token= '5681872559:AAHCdrgJVnNJW2PKjF4eApmk8ik-hPg3Iwc'
    # bot = Bot(os.getenv("BOT_TOKEN"), 2)
    bot = Bot(token, 2)
    try:
        print('bot has been started')
        loop.create_task(bot.start())
        loop.run_forever()
    except KeyboardInterrupt:
        print("\nstopping", datetime.now())
        loop.run_until_complete(bot.stop())
        print('bot has been stopped', datetime.now())


if __name__ == '__main__':
    run_bot()
