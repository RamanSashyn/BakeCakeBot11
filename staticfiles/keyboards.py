from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def get_consent_keyboard():
    """Создает клавиатуру с кнопками согласия и отказа."""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Согласен с обработкой персональных данных")],
            [KeyboardButton(text="Не согласен с обработкой персональных данных")]
        ],
        resize_keyboard=True
    )
    return keyboard


def get_main_menu():
    """Главное меню с кнопками (InlineKeyboard)."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Хочу заказать торт", callback_data="order_cake")],
            [InlineKeyboardButton(text="Просмотреть цены и описание тортов", callback_data="view_prices")]
        ]
    )


def get_order_menu():
    """Меню выбора типа заказа торта."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Заказать готовый торт", callback_data="order_ready_cake")],
            [InlineKeyboardButton(text="Заказать кастомный торт", callback_data="order_custom_cake")]
        ]
    )


def get_ready_cakes_menu():
    """Меню с выбором готовых тортов."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Торт "Ореховый шедевр"', callback_data="cake_nut_masterpiece")],
            [InlineKeyboardButton(text='Торт "Тропический рай"', callback_data="cake_tropical_paradise")],
            [InlineKeyboardButton(text='Торт "Медовик по-домашнему"', callback_data="cake_honey_homemade")],
            [InlineKeyboardButton(text='Торт "Клубничная мечта"', callback_data="cake_strawberry_dream")],
            [InlineKeyboardButton(text='Торт "Шоколадное наслаждение"', callback_data="cake_choco_delight")]
        ]
    )