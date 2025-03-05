from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from django.db.models import QuerySet
from bot.models import StandardCake, CustomCake
from asgiref.sync import sync_to_async


def get_consent_keyboard():
    """Создает клавиатуру с кнопками согласия и отказа."""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅Согласен с обработкой персональных данных")],
            [KeyboardButton(text="❌Не согласен с обработкой персональных данных")],
        ],
        resize_keyboard=True,
    )
    return keyboard


def get_main_menu():
    """Главное меню с кнопками (InlineKeyboard)."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🎂Хочу заказать торт", callback_data="order_cake"
                )
            ],
            [
                InlineKeyboardButton(
                    text="💰Просмотреть цены и описание тортов",
                    callback_data="view_prices",
                )
            ],
            [
                InlineKeyboardButton(
                    text="📬Узнать сроки доставки", callback_data="delivery_time"
                )
            ],
        ]
    )


def get_order_menu():
    """Меню выбора типа заказа торта."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🎂Заказать готовый торт", callback_data="order_ready_cake"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🎨Заказать кастомный торт", callback_data="order_custom_cake"
                )
            ],
        ]
    )


@sync_to_async
def get_cakes_from_db():
    try:
        return list(StandardCake.objects.all())
    except Exception as e:
        print(f"Error: {e}")
        return []


async def get_ready_cakes_menu():
    """Меню с выбором готовых тортов."""
    cakes = await get_cakes_from_db()

    # Создаем клавиатуру
    inline_buttons = []

    for cake in cakes:
        button_text = f"🍰 {cake.name} - {cake.price} руб."
        callback_data = (
            f"cake_{cake.id}"  # Используем ID торта в качестве callback_data
        )
        inline_buttons.append(
            InlineKeyboardButton(text=button_text, callback_data=callback_data)
        )

    # Разбиваем кнопки на строки (например, по 2 кнопки в строке)
    row_width = 2
    rows = [
        inline_buttons[i : i + row_width]
        for i in range(0, len(inline_buttons), row_width)
    ]

    return InlineKeyboardMarkup(inline_keyboard=rows)


@sync_to_async
def get_all_custom_cakes():
    """Получает список всех кастомных тортов из базы данных."""
    try:
        return list(CustomCake.objects.all())
    except Exception as e:
        print(f"Ошибка при получении кастомных тортов: {e}")
        return []


def get_level_keyboard():
    # Получаем все доступные уровни из LEVEL_CHOICES
    level_choices = dict(CustomCake.LEVEL_CHOICES)

    buttons = [
        [InlineKeyboardButton(text=level_text, callback_data=f"level_{level_value}")]
        for level_value, level_text in level_choices.items()
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    return keyboard


def get_shape_keyboard():
    """Создаем клавиатуру для выбора формы торта"""
    # Предположим, что ваш CustomCake имеет поле SHAPE_CHOICES, где хранятся формы
    shape_choices = dict(CustomCake.SHAPE_CHOICES)

    # Создаем кнопки
    buttons = [
        [InlineKeyboardButton(text=shape_text, callback_data=f"shape_{shape_value}")]
        for shape_value, shape_text in shape_choices.items()
    ]

    # Инициализируем InlineKeyboardMarkup с кнопками
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def get_topping_keyboard():
    """Создаем клавиатуру для выбора топпинга торта"""
    # Предположим, что ваш CustomCake имеет поле TOPPING_CHOICES, где хранятся топпинги
    topping_choices = dict(CustomCake.TOPPING_CHOICES)

    # Создаем кнопки
    buttons = [
        [
            InlineKeyboardButton(
                text=topping_text, callback_data=f"topping_{topping_value}"
            )
        ]
        for topping_value, topping_text in topping_choices.items()
    ]

    # Инициализируем InlineKeyboardMarkup с кнопками
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def get_berries_keyboard():
    """Создаем клавиатуру для выбора ягод"""
    # Предположим, что ваш CustomCake имеет поле BERRY_CHOICES, где хранятся ягоды
    berry_choices = dict(CustomCake.BERRY_CHOICES)

    # Создаем кнопки
    buttons = [
        [InlineKeyboardButton(text=berry_text, callback_data=f"berry_{berry_value}")]
        for berry_value, berry_text in berry_choices.items()
    ]

    # Инициализируем InlineKeyboardMarkup с кнопками
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def get_decor_keyboard():
    """Создаем клавиатуру для выбора декора"""
    # Предположим, что ваш CustomCake имеет поле DECOR_CHOICES, где хранятся декоры
    decor_choices = dict(CustomCake.DECOR_CHOICES)

    # Создаем кнопки
    buttons = [
        [InlineKeyboardButton(text=decor_text, callback_data=f"decor_{decor_value}")]
        for decor_value, decor_text in decor_choices.items()
    ]

    # Инициализируем InlineKeyboardMarkup с кнопками
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard
