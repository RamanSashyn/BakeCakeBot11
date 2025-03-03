from django.db import models
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime, timedelta
from django.utils.timezone import now
from django.utils import timezone
from decimal import Decimal
from .vk_utils import generate_vk_short_link, count_clicks


ACCESS_TOKEN = '1fe567ad1fe567ad1fe567adf51cce744a11fe51fe567ad785a30ef24c275e663c9b6b6'


class User(models.Model):
    name = models.CharField(max_length=100, verbose_name='Имя')
    surname = models.CharField(max_length=100, verbose_name='Фамилия')
    address = models.CharField(max_length=255, verbose_name='Адрес')
    phone_number = models.CharField(max_length=15, verbose_name="Номер телефона", unique=True)

    def __str__(self):
        return f"{self.name} {self.surname} ({self.phone_number})"


class Cake(models.Model):

    class Meta:
        abstract = True


    level = models.ForeignKey('Level', on_delete=models.CASCADE, verbose_name='Уровень')
    shape = models.ForeignKey('Shape', on_delete=models.CASCADE, verbose_name="Форма торта")
    topping = models.ForeignKey('Topping', on_delete=models.CASCADE, null=True, blank=True, verbose_name='Топинг')
    berries = models.ManyToManyField('Berry', blank=True, verbose_name='Ягоды')
    decor = models.ManyToManyField('Decor', blank=True, verbose_name='Декор')
    inscription = models.CharField(max_length=200, blank=True, null=True, verbose_name="Надпись (+500 руб.)")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Цена", editable=False)

    def set_price_cake(self):
        level = self.level.price
        shape_price = self.shape.price
        topping_price = self.topping.price if self.topping else 0
        berries_price = sum(berry.price for berry in self.berries.all())
        decor_price = sum(decor.price for decor in self.decor.all())
        inscription_price = 500 if self.inscription else 0

        self.price = level + shape_price + topping_price + berries_price + decor_price + inscription_price

    def save(self, *args, **kwargs):
        """Пересчет цены перед сохранением"""
        super().save(*args, **kwargs)
        self.set_price_cake()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Торт {self.level} уровня(ей), {self.shape}, {self.topping} - цена {self.price}"


class StandardCake(Cake):
    """Модель для стандартных тортов"""
    name = models.CharField(max_length=100, unique=True, verbose_name="Название торта", default="")
    description = models.TextField(verbose_name="Описание торта", blank=True, null=True)

    def __str__(self):
        return f"{self.name} уровня(ей) {self.level}, форма {self.shape} - цена {self.price}"


class CustomCake(Cake):
    """Модель для кастомных тортов, где пользователь может выбрать ингредиенты"""

    def __str__(self):
        return f"Кастомный торт {self.level} уровня(ей), {self.shape} - цена {self.price}"


class BaseChoiceModel(models.Model):
    """Абстрактная модель для автоустановки цены по CHOICES."""
    name = models.CharField(max_length=50, unique=True, verbose_name="Название")
    price = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Цена", editable=False)

    CHOICES = []  # Должен переопределяться в дочерних классах

    #

    class Meta:
        abstract = True

    #     ordering = ["name"]

    def set_price(self):
        for choice in self.CHOICES:
            if choice[0] == self.name:
                self.price = choice[2]
                return

    def save(self, *args, **kwargs):
        """Устанавливает цену на основе CHOICES"""
        self.set_price()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} (+{self.price} руб.)"


class Topping(BaseChoiceModel):
    CHOICES = [
        ('none', 'Без топпинга', 0), ('white_sauce', 'Белый соус', 200), ('caramel_syrup', 'Карамельный сироп', 180),
        ('maple_syrup', 'Кленовый сироп', 200), ('strawberry_syrup', 'Клубничный сироп', 300),
        ('blueberry_syrup', 'Черничный сироп', 350), ('milk_chocolate', 'Молочный шоколад', 200)
    ]

    name = models.CharField(
        max_length=50,
        choices=[(t[0], t[1]) for t in CHOICES],
        unique=True,
        verbose_name="Топпинг"
    )


class Berry(BaseChoiceModel):
    CHOICES = [
        ('blackberry', 'Ежевика', 400), ('raspberry', 'Малина', 300),
        ('blueberry', 'Голубика', 450), ('strawberry', 'Клубника', 500)
    ]

    name = models.CharField(
        max_length=50,
        choices=[(b[0], b[1]) for b in CHOICES],
        unique=True,
        verbose_name="Ягоды"
    )


class Shape(BaseChoiceModel):
    CHOICES = [
        ('square', 'Квадрат', 600), ('circle', 'Круг', 400), ('rectangle', 'Прямоугольник', 1000)
    ]

    name = models.CharField(
        max_length=50,
        choices=[(s[0], s[1]) for s in CHOICES],
        unique=True,
        verbose_name="Форма торта"
    )


class Level(BaseChoiceModel):
    CHOICES = [('1', '1 уровень', 400), ('2', '2 уровня', 750), ('3', '3 уровня', 1100)]

    name = models.CharField(
        max_length=50,
        choices=[(l[0], l[1]) for l in CHOICES],
        unique=True,
        verbose_name="Уровень"
    )


class Decor(BaseChoiceModel):
    CHOICES = [('pistachios', 'фисташки ', 300), ('meringue', 'безе', 400), ('hazelnut', 'фундук', 350),
               ('pecan', 'пекан', 300), ('marshmallow', 'маршмеллоу', 200), ('marzipan', 'марципан', 280)]

    name = models.CharField(
        max_length=50,
        choices=[(d[0], d[1]) for d in CHOICES],
        unique=True,
        verbose_name="Декор"
    )


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Заказчик')
    standard_cake = models.ForeignKey(StandardCake, null=True, blank=True, on_delete=models.CASCADE,
                                      verbose_name="Стандартный торт")
    custom_cake = models.ForeignKey(CustomCake, null=True, blank=True, on_delete=models.CASCADE,
                                    verbose_name="Кастомный торт")
    address = models.CharField(max_length=255, verbose_name="Адрес доставки")
    order_date = models.DateField(verbose_name='Дата заказа', default=timezone.now)
    delivery_date = models.DateField(verbose_name="Дата доставки", default=now)
    delivery_time = models.TimeField(verbose_name="Время доставки")
    comment = models.TextField(blank=True, verbose_name="Комментарий")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена", editable=False, default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)


    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.address:
            self.address = self.user.address

        today = timezone.now().date()

        # Проверяем, какой торт выбран
        if self.standard_cake and self.custom_cake:
            cake_price = self.standard_cake.price + self.custom_cake.price
        elif self.standard_cake:
            cake_price = self.standard_cake.price
        elif self.custom_cake:
            cake_price = self.custom_cake.price
        else:
            cake_price = 0  # Если торт не выбран, чтобы избежать ошибки

        # Если доставка сегодня или завтра — цена повышается на 20%
        if self.delivery_date == today or self.delivery_date <= today + timedelta(days=1):
            self.price = cake_price * Decimal('1.2')
        else:
            self.price = cake_price

        super().save(*args, **kwargs)

    def __str__(self):
        if self.standard_cake and self.custom_cake:
            return f"Заказ № {self.id} - {self.standard_cake} и {self.custom_cake} - цена {self.price}"
        return f"Заказ № {self.id} - {self.standard_cake if self.standard_cake else self.custom_cake}"


class OrderStatistics(models.Model):
    total_orders = models.IntegerField(default=0, verbose_name='Количество заказов', editable=False)
    total_sales = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), verbose_name="Общий доход")
    averange_cost = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Средняя стоимость заказа")
    last_order_date = models.DateField(verbose_name="Дата последнего заказа", default=now)


    def update_order_statistics(self):
        all_orders = Order.objects.all()

        self.total_orders = all_orders.count()
        self.total_sales = sum(order.price for order in all_orders)
        self.averange_cost = self.total_sales / self.total_orders

        last_order = all_orders.order_by('-order_date').first()
        self.last_order_date = last_order.order_date if last_order.order_date else None

        self.save()

    def __str__(self):
        return f"Статистика заказов: {self.total_orders} заказов, {self.total_sales} руб."


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