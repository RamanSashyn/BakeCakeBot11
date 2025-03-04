from django.db import models
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime, timedelta
from django.utils.timezone import now
from django.utils import timezone
from decimal import Decimal
from .vk_utils import generate_vk_short_link, count_clicks


ACCESS_TOKEN = '1fe567ad1fe567ad1fe567adf51cce744a11fe51fe567ad785a30ef24c275e663c9b6b6'


class StandardCake(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.name} - {self.price} руб."


class CakeOrder(models.Model):
    # Связь с моделью StandardCake для выбранного торта
    cake = models.ForeignKey(StandardCake, on_delete=models.SET_NULL, null=True, blank=True)

    # Текст на торте
    cake_text = models.CharField(max_length=255, blank=True, null=True)

    # Адрес доставки
    address = models.CharField(max_length=255)

    # Пожелания пользователя
    comment = models.TextField(blank=True, null=True)

    # Итоговая цена с учетом добавленных услуг (например, текст на торте)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    # Дата создания заказа
    created_at = models.DateTimeField(auto_now_add=True)

    telegram_id = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"Заказ: {self.cake.name if self.cake else 'Неизвестный торт'} - {self.price} руб."

    # Метод для расчета итоговой цены с учетом текста на торте
    def calculate_price(self):
        if self.cake_text and self.cake_text.lower() != 'нет':  # Если есть текст на торте
            return self.cake.price + 500  # Добавляем 500 рублей за текст
        return self.cake.price  # Если текста нет, цена остается как у стандартного торта


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