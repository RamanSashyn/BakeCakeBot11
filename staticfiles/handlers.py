from aiogram import types, Router, F
from aiogram.types import FSInputFile
from aiogram.filters import Command
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from datetime import datetime, timedelta
from bot.models import DeliveryState, CustomCakeState, StandardCake, CakeOrder, CustomCake
from asgiref.sync import sync_to_async
import logging
from asgiref.sync import sync_to_async
from aiogram import Bot, types
from config import ADMIN_GROUP_ID
from .keyboards import (
    get_consent_keyboard,
    get_main_menu,
    get_order_menu,
    get_ready_cakes_menu,
    get_level_keyboard,
    get_shape_keyboard,
    get_topping_keyboard,
    get_berries_keyboard,
    get_decor_keyboard,
)
from .notifications import send_order_notification

router = Router()


@router.message(Command("get_group_id"))
async def get_group_id(message: types.Message):
    """Отправляет ID группы"""
    if message.chat.type in ["group", "supergroup"]:
        await message.answer(
            f"ID этой группы: `{message.chat.id}`", parse_mode="Markdown"
        )
    else:
        await message.answer("Эта команда работает только в группах!")


async def send_admin_notification(bot: Bot, text: str):
    """Отправляет уведомление в группу администраторов"""
    await bot.send_message(ADMIN_GROUP_ID, text)


@router.message(Command("start"))
async def send_welcome(message: types.Message):
    """Отправляет приветственное сообщение с кнопками согласия."""
    user_name = (
        message.from_user.username
        if message.from_user.username
        else message.from_user.first_name
    )
    text = f"Привет, {user_name} 🙋‍♀️! BakeCake приветствует тебя. Для продолжения работы, пожалуйста, подтвердите согласие с обработкой персональных данных."
    consent_file = FSInputFile("files/soglasie.pdf")
    await message.answer(text, reply_markup=get_consent_keyboard())
    await message.answer_document(consent_file)


@router.message(
    lambda message: message.text == "✅Согласен с обработкой персональных данных"
)
async def agree_handler(message: types.Message):
    await message.answer(
        "Вы дали согласие на обработку персональных данных. Можете продолжить работу",
        reply_markup=types.ReplyKeyboardRemove(),
    )
    """Обрабатывает согласие и показывает главное меню."""
    await message.answer(
        "Пожалуйста, выберите, что Вас интересует", reply_markup=get_main_menu()
    )


@router.message(
    lambda message: message.text == "❌Не согласен с обработкой персональных данных"
)
async def disagree_handler(message: types.Message):
    """Обрабатывает отказ и завершает диалог."""
    await message.answer(
        "Вы не согласились с обработкой персональных данных. К сожалению, мы не можем продолжить работу😔.",
        reply_markup=types.ReplyKeyboardRemove(),
    )


@router.callback_query(F.data == "order_cake")
async def order_cake_callback(callback: CallbackQuery):
    """Обрабатывает нажатие на кнопку 'Хочу заказать торт' и предлагает выбрать тип заказа."""
    await callback.message.answer(
        "Какой торт хотите заказать?", reply_markup=get_order_menu()
    )


@sync_to_async
def get_all_cakes():
    try:
        return list(
            StandardCake.objects.all())
    except Exception as e:
        print(f"Error: {e}")
        return []

@router.callback_query(F.data == "view_prices")
async def view_prices_callback(callback: CallbackQuery):
    """Обрабатывает нажатие на кнопку 'Просмотреть цены'."""
    cakes = await get_all_cakes()
    price_list= "Вот наш прайс-лист:\n"

    for index, cake in enumerate(cakes, start=1):
        price_list += f"{index}. {cake.name}\n" \
                      f"Описание: {cake.description}\n" \
                      f"Цена: {cake.price} руб.\n\n"
    await callback.message.answer(price_list)


@router.callback_query(F.data == "delivery_time")
async def delivery_time_callback(callback: CallbackQuery):
    """Выдает пользователю дату доставки (текущая + 2 дня)."""
    delivery_date = (datetime.now() + timedelta(days=2)).strftime("%d.%m.%Y")
    await callback.message.answer(f"📦 Ориентировочная дата доставки: {delivery_date}")


@router.callback_query(F.data == "order_ready_cake")
async def order_ready_cake_callback(callback: CallbackQuery):
    """Обрабатывает нажатие на кнопку 'Заказать готовый торт' и показывает список тортов."""

    reply_markup = await get_ready_cakes_menu()

    await callback.message.answer(
        "Выберите один из наших готовых тортов:", reply_markup=reply_markup
    )


@sync_to_async
def get_cake_by_id(cake_id):
    try:
        return StandardCake.objects.get(id=cake_id)
    except StandardCake.DoesNotExist:
        return None


@router.callback_query(F.data.startswith("cake_"))
async def ready_cake_selected(callback: CallbackQuery, state: FSMContext):
    """Обрабатывает выбор готового торта и запрашивает текст надписи."""

    cake_id = callback.data.split("_")[1]  # Получаем ID торта из callback_data
    selected_cake = await get_cake_by_id(cake_id)  # Получаем торт из базы асинхронно

    if selected_cake:
        await state.update_data(selected_cake=f"Торт '{selected_cake.name}' - {selected_cake.price} руб.")
        await callback.message.answer(
            f"✅ Вы выбрали торт *{selected_cake.name}*.",
            parse_mode="Markdown",
        )

        await callback.message.answer(
            "Теперь напишите текст, который хотите на торт (или напишите 'нет', если без надписи)."
        )

        await state.update_data(selected_cake_id=cake_id)

        await state.set_state(CustomCakeState.waiting_for_text)
    else:
        await callback.message.answer("❌ Не удалось найти выбранный торт.")

    await callback.answer()


@router.callback_query(F.data == "start_delivery")
async def start_delivery(callback: CallbackQuery, state: FSMContext):
    """Начинаем процесс оформления доставки."""
    await callback.message.answer("📍Пожалуйста, введите адрес доставки:")
    await state.set_state(DeliveryState.waiting_for_address)


@router.message(DeliveryState.waiting_for_address)
async def process_address(message: types.Message, state: FSMContext):
    """Сохраняем адрес и запрашиваем комментарий."""
    await state.update_data(address=message.text)
    await message.answer(
        "Спасибо! Теперь введите ваши пожелания (если есть). Если пожеланий нет, просто напишите 'нет'."
    )
    await state.set_state(DeliveryState.waiting_for_comment)


@sync_to_async
def save_order(cake_order):
    cake_order.save()


@router.message(DeliveryState.waiting_for_comment)
async def process_comment(message: types.Message, state: FSMContext, bot: Bot):
    """Сохраняем комментарий, завершаем процесс заказа и уведомляет администраторов."""
    user_data = await state.get_data()
    address = user_data.get("address")
    comment = message.text
    selected_cake_id = user_data.get("selected_cake_id")
    cake_text = user_data.get("cake_text", None)

    if selected_cake_id:
        # Ищем готовый торт в базе данных
        selected_cake = await get_cake_by_id(selected_cake_id)
        if not selected_cake:
            await message.answer("❌ Ошибка: выбранный торт не найден. Попробуйте снова.")
            return
        cake_price = selected_cake.price
        cake_name = selected_cake.name
    else:
        # Создаём кастомный торт, если ID нет (значит, пользователь выбрал кастомный вариант)
        selected_cake = CustomCake(
            levels=user_data.get("level", 1),
            shape=user_data.get("shape", "round"),
            topping=user_data.get("topping", "none"),
            berries=user_data.get("berry", "none"),
            decor=user_data.get("decor", "none"),
            cake_text=cake_text
        )
        cake_price = selected_cake.calculate_price()
        cake_name = "Кастомный торт"

    # Создаём заказ
    cake_order = CakeOrder(
        cake=selected_cake if selected_cake_id else None,  # Привязываем готовый торт, если он есть
        cake_text=cake_text,
        address=address,
        comment=comment,
        price=cake_price,
        telegram_id=message.from_user.username,
    )
    await save_order(cake_order)

    await message.answer(
        f"✅ Ваш заказ оформлен!\n\n"
        f"Вы выбрали: {cake_name} - {cake_price} руб.\n"
        f"Дополнительно: {'Текст на торте: ' + cake_text if cake_text else 'Без надписи'}\n"
        f"📍 Адрес доставки: {address}\n"
        f"💬 Пожелания: {comment}\n\n"
        f"Спасибо, что выбрали нас! 🎂"
    )

    await send_order_notification(
        bot, message.from_user, cake_name, address, comment, cake_text
    )

    await state.clear()






@router.callback_query(F.data == "order_custom_cake")
async def order_custom_cake_callback(callback: CallbackQuery):
    """Запуск кастомизации торта и выбор уровня"""
    await callback.message.answer(
        "Выберите уровень торта:",
        reply_markup=get_level_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("level_"))
async def level_selected(callback: CallbackQuery, state: FSMContext):
    """Обрабатываем выбор уровня торта"""
    level = callback.data.split("_")[1]

    await state.update_data(level=level)

    await state.set_state(CustomCakeState.waiting_for_shape)

    await callback.message.answer(
        f"Вы выбрали: {level} уровень. 🎂\nТеперь выберите форму торта.",
        reply_markup=get_shape_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("shape_"))
async def shape_selected(callback: CallbackQuery, state: FSMContext):
    """Обрабатываем выбор формы торта"""
    shape = callback.data.split("_")[1]
    shape_name = CustomCake.get_shape_dict().get(shape, shape)  # Получаем название из модели

    await state.update_data(shape=shape)
    await state.set_state(CustomCakeState.waiting_for_topping)

    await callback.message.answer(
        f"Вы выбрали форму: {shape_name}. 🎂\nТеперь выберите топинг для торта.",
        reply_markup=get_topping_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("topping_"))
async def topping_selected(callback: CallbackQuery, state: FSMContext):
    """Обрабатываем выбор топинга"""
    topping = callback.data.split("_", 1)[1] 
    topping_name = CustomCake.get_topping_dict().get(topping, topping)  # Получаем название из модели

    await state.update_data(topping=topping)
    await state.set_state(CustomCakeState.waiting_for_berries)

    await callback.message.answer(
        f"Вы выбрали топинг: {topping_name}. 🍫\nТеперь выберите ягоды для торта.",
        reply_markup=get_berries_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("berry_"))
async def berry_selected(callback: CallbackQuery, state: FSMContext):
    """Обрабатываем выбор ягод"""
    berry = callback.data.split("_")[1]
    berry_name = CustomCake.get_berry_dict().get(berry, berry)  # Получаем название из модели

    await state.update_data(berry=berry)
    await state.set_state(CustomCakeState.waiting_for_decor)

    await callback.message.answer(
        f"Вы выбрали ягоду: {berry_name}. 🍓\nТеперь выберите декор для торта.",
        reply_markup=get_decor_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("decor_"))
async def decor_selected(callback: CallbackQuery, state: FSMContext):
    """Обрабатываем выбор декора"""
    decor = callback.data.split("_")[1]
    decor_name = CustomCake.get_shape_dict().get(decor, decor)  # Получаем русское название

    await state.update_data(decor=decor)

    await state.set_state(CustomCakeState.waiting_for_text)

    await callback.message.answer(
        f"Вы выбрали декор: {decor_name}. 🎉\n\n"
        "Теперь напишите текст, который хотите на торт (или напишите 'нет', если без надписи)."
    )
    await callback.answer()


@router.message(CustomCakeState.waiting_for_text)
async def receive_cake_text(message: types.Message, state: FSMContext):
    """Формируем итоговый заказ после ввода текста."""
    cake_text = message.text.strip().lower()

    if cake_text == "нет":
        cake_text = None  

    await state.update_data(cake_text=cake_text)
    user_data = await state.get_data()

    selected_cake = user_data.get("selected_cake", "Кастомный торт")

    if "Кастомный торт" in selected_cake:
        level = user_data.get("level", 1)  # По умолчанию 1 уровень
        shape = user_data.get("shape", "round")  # По умолчанию круглый
        topping = user_data.get("topping", "none")
        berry = user_data.get("berry", "none")
        decor = user_data.get("decor", "none")

        # Создаём объект кастомного торта
        custom_cake = CustomCake(
            levels=level,
            shape=shape,
            topping=topping,
            berries=berry,
            decor=decor,
            cake_text=cake_text
        )

        # Вычисляем цену через метод экземпляра
        total_price = custom_cake.calculate_price()

        result_message = (
            "🎂 *Ваш заказ готов!*\n\n"
            f"📏 Уровень: {CustomCake.get_level_dict().get(level, 'Не указан')}\n"
            f"🔵 Форма: {CustomCake.get_shape_dict().get(shape, 'Не указана')}\n"
            f"🍫 Топпинг: {CustomCake.get_topping_dict().get(topping, 'Не указан')}\n"
            f"🍓 Ягоды: {CustomCake.get_berry_dict().get(berry, 'Не указаны')}\n"
            f"✨ Декор: {CustomCake.get_decor_dict().get(decor, 'Без декора')}\n"
            f"🖋 Надпись: {cake_text or 'Без надписи'}\n"
            f"💵 Общая цена: {total_price} руб.\n\n"
            "📍 Теперь укажите адрес доставки:"
        )
    else:
        # Для обычных тортов вызываем метод класса, если он есть (добавь его в модель)
        total_price = CustomCake.calculate_price(selected_cake, cake_text)  
        result_message = (
            f"✅ Вы выбрали торт *{selected_cake}*.\n\n"
            f"🖋 Надпись: {cake_text or 'Без надписи'}\n"
            f"💵 Общая цена: {total_price} руб.\n\n"
            "📍 Теперь укажите адрес доставки:"
        )

    await message.answer(result_message, parse_mode="Markdown")
    await state.set_state(DeliveryState.waiting_for_address)




@router.message(DeliveryState.waiting_for_address)
async def receive_address(message: types.Message, state: FSMContext):
    """Сохраняем адрес и запрашиваем комментарий."""
    address = message.text
    await state.update_data(address=address)

    await message.answer(
        "Спасибо! Теперь введите ваши пожелания (если есть). Если пожеланий нет, просто напишите 'нет'."
    )

    await state.set_state(DeliveryState.waiting_for_comment)
