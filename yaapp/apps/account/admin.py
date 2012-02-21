from django.contrib import admin
from models import UserProfile, Device 

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user',)
    search_fields = ['user__username']
admin.site.register(UserProfile, UserProfileAdmin)

class DeviceAdmin(admin.ModelAdmin):
    list_display = ('user', 'uuid')
    search_fields = ['user__username', 'uuid']
admin.site.register(Device, DeviceAdmin)
    