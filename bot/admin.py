from django.contrib import admin
from .models import ShortLink
from .vk_utils import count_clicks
from .models import User, Order, Topping, Level, Decor, Berry, Shape, StandardCake, CustomCake, OrderStatistics


class CakeAdmin(admin.ModelAdmin):
    list_display = ('level', 'shape', 'topping', 'price')  # Отображаем нужные поля
    search_fields = ('level__name', 'shape__name', 'topping__name')  # Возможность поиска по полям
    filter_horizontal = ('berries', 'decor')  # Позволяет легко добавлять несколько ягод и декора


class StandardCakeAdmin(CakeAdmin):
    list_display = ('name', 'level', 'shape', 'topping', 'price')


class ShortLinkAdmin(admin.ModelAdmin):
    list_display = ('original_url', 'short_url', 'created_at', 'clicks_count')
    search_fields = ('original_url', 'short_url')
    readonly_fields = ('clicks_count',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)

        for short_link in queryset:
            clicks_count = count_clicks('1fe567ad1fe567ad1fe567adf51cce744a11fe51fe567ad785a30ef24c275e663c9b6b6',
                                        short_link.short_url)
            short_link.clicks_count = clicks_count[0] if clicks_count else 0
            short_link.save()
        return queryset

admin.site.register(ShortLink, ShortLinkAdmin)
admin.site.register(User)
admin.site.register(Order)
admin.site.register(Topping)
admin.site.register(Level)
admin.site.register(Decor)
admin.site.register(Berry)
admin.site.register(Shape)
admin.site.register(CustomCake, CakeAdmin)
admin.site.register(StandardCake, StandardCakeAdmin)
admin.site.register(OrderStatistics)
