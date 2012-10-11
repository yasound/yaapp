from django.contrib import admin
from models import Continent, Country, Radio, Genre

class ContinentAdmin(admin.ModelAdmin):
    list_display = ('name_fr', 'sigle')
admin.site.register(Continent, ContinentAdmin)

class CountryAdmin(admin.ModelAdmin):
    list_display = ('name_fr', 'sigle')
admin.site.register(Country, CountryAdmin)

class GenreAdmin(admin.ModelAdmin):
    list_display = ('name_fr',)
admin.site.register(Genre, GenreAdmin)

class RadioAdmin(admin.ModelAdmin):
    list_display = ('radioways_id', 'name', 'rtype', 'stream_codec', 'country')
    raw_id_fields = ('yasound_radio',)
admin.site.register(Radio, RadioAdmin)
