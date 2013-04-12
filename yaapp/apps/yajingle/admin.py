from django.contrib import admin
from models import Jingle


class JingleAdmin(admin.ModelAdmin):
    list_display = ('name', 'filename', 'jtype')
    search_fields = ('name',)
    list_filter = ('jtype',)
    raw_id_fields = ('creator',)
admin.site.register(Jingle, JingleAdmin)

