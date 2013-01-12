from django.contrib import admin
from models import BlogPost


class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('name_en', 'name_fr', 'state', )
    list_filter = ('state', )
    prepopulated_fields = {'slug': ('name_en',)}
    search_fields = ['name_en', 'description_en']
admin.site.register(BlogPost, BlogPostAdmin)
