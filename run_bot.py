import asyncio
from aiogram import Bot, Dispatcher
from staticfiles.handlers import router

TOKEN = "7996830180:AAG7WWT5MOKU8s40MfCxrAKMeYyulVh-BPM"

async def main():
    bot = Bot(token=TOKEN)
    dp = Dispatcher()

    # Регистрируем роутер с обработчиками
    dp.include_router(router)

    print("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
