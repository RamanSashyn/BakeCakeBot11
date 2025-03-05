import os
import django

# Устанавливаем настройки Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cake_bot.settings")

# Инициализируем Django
django.setup()

import asyncio
from aiogram import Bot, Dispatcher
from staticfiles.handlers import router  # Если это необходимо

# Импортируйте ваш бот и другие компоненты только после настройки Django
TOKEN = "7496626388:AAH3n8g35MqRRLw_E9kyGvvr87fLrU63HBQ"


async def main():
    bot = Bot(token=TOKEN)
    dp = Dispatcher()

    # Регистрируем роутер с обработчиками
    dp.include_router(router)

    print("Бот запущен!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
