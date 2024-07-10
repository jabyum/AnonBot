from aiogram import Bot, Dispatcher
import asyncio
from bot import bot_router
from admin import admin_router
from database import Base, engine
# TODO токен
bot = Bot(token="7179376455:AAGRR3yoigTPoyUdvOv89ObUteusWVFH8Y8")
dp = Dispatcher()
Base.metadata.create_all(bind=engine)

async def main():
    dp.include_router(admin_router)
    dp.include_router(bot_router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())