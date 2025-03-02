from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order, OrderStatistics

@receiver(post_save, sender=Order)
def update_order_statistics(sender, instance, **kwargs):
    stats, created = OrderStatistics.objects.get_or_create(id=1)  # Одна запись на все заказы
    stats.update_order_statistics()