from django.contrib import admin
from models import RadioListeningStat

class RadioListeningStatAdmin(admin.ModelAdmin):
    list_display = ('radio', 'overall_listening_time', 'audience', 'favorites', 'likes', 'dislikes', 'date')
    search_fields = ( 'radio', )
    list_filter = ('radio', 'date')
admin.site.register(RadioListeningStat, RadioListeningStatAdmin)
