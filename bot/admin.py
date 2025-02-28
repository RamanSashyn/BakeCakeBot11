from django.contrib import admin
from .models import ShortLink
from .vk_utils import count_clicks


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
