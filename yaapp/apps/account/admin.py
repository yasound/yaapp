from django.contrib import admin
from models import UserProfile, Device 
from sorl.thumbnail.admin import AdminImageMixin

class UserProfileAdmin(AdminImageMixin, admin.ModelAdmin):
    list_display = ('id', 'user', 'name')
    search_fields = ['user__username']
admin.site.register(UserProfile, UserProfileAdmin)

class DeviceAdmin(admin.ModelAdmin):
    list_display = ('user', 'ios_token')
    search_fields = ['user__username', 'ios_token']
admin.site.register(Device, DeviceAdmin)
    