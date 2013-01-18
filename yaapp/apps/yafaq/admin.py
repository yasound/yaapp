from django.contrib import admin
from models import FaqEntry


class FaqEntryAdmin(admin.ModelAdmin):
    list_display = ('title_en', 'title_fr', 'order', )
    search_fields = ['title_en', 'content_en']
    list_editable = ('order',)
admin.site.register(FaqEntry, FaqEntryAdmin)
