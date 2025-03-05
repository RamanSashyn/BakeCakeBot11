from django.db import models
from aiogram.fsm.state import State, StatesGroup
from django.utils.timezone import now
from .vk_utils import generate_vk_short_link, count_clicks

ACCESS_TOKEN = '1fe567ad1fe567ad1fe567adf51cce744a11fe51fe567ad785a30ef24c275e663c9b6b6'


class StandardCake(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.name} - {self.price} руб."


class CustomCake(models.Model):
    SHAPE_CHOICES = [
        ('round', 'Круглый'),
        ('square', 'Квадратный'),
        ('heart', 'Сердце'),
    ]

    LEVEL_CHOICES = [
        (1, '1 уровень'),
        (2, '2 уровня'),
        (3, '3 уровня'),
    ]

    TOPPING_CHOICES = [
        ('chocolate', 'Шоколадный'),
        ('caramel', 'Карамельный'),
        ('berry', 'Ягодный'),
        ('none', 'Без топпинга')
    ]

    BERRY_CHOICES = [
        ('strawberry', 'Клубника'),
        ('raspberry', 'Малина'),
        ('blueberry', 'Голубика'),
        ('none', 'Без ягод'),
    ]

    DECOR_CHOICES = [
        ('nuts', 'Орехи'),
        ('cookies', 'Печенье'),
        ('marshmallow', 'Зефир'),
        ('none', 'Без декора'),
    ]

    order = models.OneToOneField('CakeOrder', on_delete=models.CASCADE, related_name='custom_cake', verbose_name="Заказ", null=True, blank=True)

    shape = models.CharField(max_length=20, choices=SHAPE_CHOICES, verbose_name="Форма")
    levels = models.IntegerField(choices=LEVEL_CHOICES, verbose_name="Уровни")
    topping = models.CharField(max_length=20, choices=TOPPING_CHOICES, verbose_name="Топпинг")
    berries = models.CharField(max_length=20, choices=BERRY_CHOICES, verbose_name="Ягоды", default='none')
    decor = models.CharField(max_length=20, choices=DECOR_CHOICES, default='none', verbose_name="Декор")

    cake_text = models.CharField(max_length=255, blank=True, null=True, verbose_name="Надпись")

    price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Цена")

    @classmethod
    def get_shape_dict(cls):
        return dict(cls.SHAPE_CHOICES)

    @classmethod
    def get_level_dict(cls):
        return dict(cls.LEVEL_CHOICES)

    @classmethod
    def get_topping_dict(cls):
        return dict(cls.TOPPING_CHOICES)

    @classmethod
    def get_berry_dict(cls):
        return dict(cls.BERRY_CHOICES)

    @classmethod
    def get_decor_dict(cls):
        return dict(cls.DECOR_CHOICES)
    
    def calculate_price(self):
        base_price = 2000  # Базовая цена кастомного торта

        # Увеличение цены в зависимости от уровней
        if self.levels == 2:
            base_price += 1000
        elif self.levels == 3:
            base_price += 2000

        # Добавление стоимости за топпинг
        base_price += 300

        # Добавление стоимости за ягоды, если они есть
        if self.berries != 'none':
            base_price += 500

        # Добавление стоимости за декор
        if self.decor != 'none':
            base_price += 400

        # Добавление стоимости за текст на торте
        if self.cake_text and self.cake_text.lower() != 'нет':
            base_price += 500

        self.price = base_price
        return self.price

    def save(self, *args, **kwargs):
        self.calculate_price()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Кастомный торт ({self.levels} уровня, {self.shape}) - {self.price} руб."

class CakeOrder(models.Model):
    cake = models.ForeignKey(StandardCake, on_delete=models.SET_NULL, null=True, blank=True)
    cake_text = models.CharField(max_length=255, blank=True, null=True, )  # Добавляем это поле
    address = models.CharField(max_length=255)
    comment = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    def calculate_price(self):
        if self.cake:
            self.price = self.cake.price
            if hasattr(self, 'custom_cake') and self.custom_cake:
                self.price += self.custom_cake.price
        return self.price

    def save(self, *args, **kwargs):
        self.calculate_price()
        super().save(*args, **kwargs)

    def __str__(self):
        if self.cake:
            return f"Заказ: {self.cake.name} - {self.price} руб."
        elif hasattr(self, 'custom_cake') and self.custom_cake:
            return f"Заказ: Кастомный торт - {self.price} руб."
        return f"Заказ: Без торта - {self.price} руб."


class DeliveryState(StatesGroup):
    waiting_for_address = State()
    waiting_for_comment = State()
    waiting_for_text = State()


class CustomCakeState(StatesGroup):
    waiting_for_level = State()
    waiting_for_shape = State()
    waiting_for_topping = State()
    waiting_for_berries = State()
    waiting_for_decor = State()
    waiting_for_text = State()
    waiting_for_address = State()
    waiting_for_message = State()


class ShortLink(models.Model):
    original_url = models.URLField()
    short_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    clicks_count = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.short_url:
            self.short_url = generate_vk_short_link(self.original_url)
        super().save(*args, **kwargs)

    def get_clicks_count(self):
        clicks = count_clicks(ACCESS_TOKEN, self.short_url)
        self.clicks_count = clicks[0] if clicks else 0
        self.save(update_fields=['clicks_count'])

    def __str__(self):
        return self.short_url
