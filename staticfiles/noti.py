from config import ADMIN_GROUP_ID
from aiogram import Bot, types

async def send_order_notification(bot: Bot, user: types.User, cake_name: str, cake_text: str = None):
    """Отправляет уведомление о новом заказе в группу администраторов."""
    try:
        text = (
            f"📢 *Новый заказ!*\n\n"
            f"🎂 Торт: *{cake_name}*\n"
            f"👤 Заказчик: @{user.username} ({user.full_name})"
        )
        if cake_text:
            text += f"\n🖋 Надпись: \"{cake_text}\""

        await bot.send_message(ADMIN_GROUP_ID, text, parse_mode="Markdown")
    except Exception as e:
        print(f"Ошибка при отправке уведомления: {e}")
