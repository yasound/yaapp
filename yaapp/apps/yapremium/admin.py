from django.contrib import admin
from models import Service, Subscription, UserSubscription, UserService, Gift, Achievement, Promocode, UserPromocode

class ServiceAdmin(admin.ModelAdmin):
    list_display = ('stype',)
admin.site.register(Service, ServiceAdmin)

class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name_en', 'sku_en', 'duration', 'enabled')
    search_fields = ( 'name_en', 'sku_en', )
admin.site.register(Subscription, SubscriptionAdmin)

class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'created', 'user', 'subscription')
    search_fields = ( 'user__username', 'user__email', 'user__user_profile__name')
admin.site.register(UserSubscription, UserSubscriptionAdmin)

class UserServiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'service','active', 'expiration_date')
    search_fields = ( 'user__username', 'user__email', 'user__user_profile__name')
admin.site.register(UserService, UserServiceAdmin)

class GiftAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'sku',
        'name_en',
        'action',
        'service',
        'duration',
        'duration_unit',
        'max_per_user',
        'delay',
        'enabled',
        'authentication_needed',
    )
    list_editable = ('enabled',)
    list_filter = ('enabled', 'authentication_needed')
admin.site.register(Gift, GiftAdmin)

class AchievementAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'gift', 'achievement_date',)
    search_fields = ( 'user__username', 'user__email', 'user__user_profile__name')
admin.site.register(Achievement, AchievementAdmin)

class PromocodeAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'service', 'duration', 'duration_unit', 'enabled', 'unique')
admin.site.register(Promocode, PromocodeAdmin)

class UserPromocodeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'promocode', 'usage_date',)
admin.site.register(UserPromocode, UserPromocodeAdmin)
