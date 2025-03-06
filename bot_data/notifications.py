from config import ADMIN_GROUP_ID
from aiogram import Bot, types


async def send_order_notification(
    bot: Bot,
    user: types.User,
    cake_name: str,
    address: str,
    comment: str = None,
    cake_text: str = None,
):
    """Отправляет уведомление о новом заказе в группу администраторов."""
    try:
        # Проверяем, кастомный ли это торт
        if "(кастомный)" in cake_name:
            cake_display_name = f"{cake_name}"
        else:
            cake_display_name = f'Заказ: "{cake_name}"'

        # Формируем текст уведомления
        text = (
            f"📢 *Новый заказ!*\n\n"
            f"🎂 *{cake_display_name}*\n"
            f"📍 *Адрес доставки:* {address}\n"
            f"👤 *Заказчик:* @{user.username if user.username else user.full_name} ({user.full_name})"
        )

        if cake_text:
            text += f'\n🖋 *Надпись:* "{cake_text}"'
        if comment and comment.lower() != "нет":
            text += f'\n💬 *Комментарий:* "{comment}"'

        # Отправляем в группу
        await bot.send_message(ADMIN_GROUP_ID, text, parse_mode="Markdown")
    except Exception as e:
        print(f"Ошибка при отправке уведомления: {e}")
