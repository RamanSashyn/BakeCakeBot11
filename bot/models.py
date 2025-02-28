from django.db import models
from aiogram.fsm.state import State, StatesGroup
from .vk_utils import generate_vk_short_link, count_clicks


ACCESS_TOKEN = '1fe567ad1fe567ad1fe567adf51cce744a11fe51fe567ad785a30ef24c275e663c9b6b6'


class DeliveryState(StatesGroup):
    waiting_for_address = State()
    waiting_for_comment = State()


class CustomCakeState(StatesGroup):
    waiting_for_text = State()
    waiting_for_address = State()


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