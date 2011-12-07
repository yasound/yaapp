from models import UserProfile
from django.contrib import admin

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'twitter_account', 'facebook_account')
    search_fields = ['user__username', 'twitter_account', 'facebook_account',]
admin.site.register(UserProfile)

