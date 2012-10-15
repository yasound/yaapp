from django.contrib import admin
from models import RadioListeningStat

class RadioListeningStatAdmin(admin.ModelAdmin):
    list_display = ('radio', 'overall_listening_time', 'audience_peak', 'connections', 'favorites', 'likes', 'dislikes', 'date')
    search_fields = ( 'radio__name', )
    raw_id_fields = ('radio',)
admin.site.register(RadioListeningStat, RadioListeningStatAdmin)
