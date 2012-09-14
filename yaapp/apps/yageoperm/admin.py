from django.contrib import admin
from models import Country, GeoFeature

class CountryAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')
admin.site.register(Country, CountryAdmin)

class GeoFeatureAdmin(admin.ModelAdmin):
    list_display = ('country', 'feature')
admin.site.register(GeoFeature, GeoFeatureAdmin)
