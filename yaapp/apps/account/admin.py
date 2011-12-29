from models import UserProfile
from django.contrib import admin

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user')
    search_fields = ['user__username']
admin.site.register(UserProfile)

