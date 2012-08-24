from django.contrib import admin
from models import Service, Subscription, UserSubscription, GiftRule, Achievement

class ServiceAdmin(admin.ModelAdmin):
    list_display = ('stype',)
admin.site.register(Service, ServiceAdmin)

class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'duration', 'enabled')
    search_fields = ( 'name', 'sku', )
admin.site.register(Subscription, SubscriptionAdmin)

class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'subscription', 'achievement', 'active', 'expiration_date')
    search_fields = ( 'user__username', 'user__email', 'user__user_profile__name')
admin.site.register(UserSubscription, UserSubscriptionAdmin)

class GiftRuleAdmin(admin.ModelAdmin):
    list_display = ('id', 'action', 'gift', 'unit', 'max_per_user')
admin.site.register(GiftRule, GiftRuleAdmin)

class AchievementAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'rule', 'achievement_date',)
    search_fields = ( 'user__username', 'user__email', 'user__user_profile__name')
admin.site.register(Achievement, AchievementAdmin)
