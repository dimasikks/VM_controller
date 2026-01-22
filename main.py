import asyncio
import os
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

load_dotenv(".main_env")
load_dotenv(".middleware_env")

import middleware
from handlers import register_handlers

BOT_TOKEN = os.getenv("BOT_TOKEN")
ACCESS_IDS_SEPARATOR = os.getenv("ACCESS_ID_SEPARATOR")
ACCESS_IDS = [int(ID) for ID in os.getenv("ACCESS_ID").split(ACCESS_IDS_SEPARATOR)]

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    dp.message.middleware(middleware.AuthMiddleware(ACCESS_IDS))
    dp.callback_query.middleware(middleware.AuthMiddleware(ACCESS_IDS))

    register_handlers(dp)

    print("✅ Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())