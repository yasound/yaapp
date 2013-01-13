from django.contrib import admin
from models import BlogPost
from wysihtml5.admin import AdminWysihtml5TextFieldMixin
from attachments.admin import AttachmentInlines


class BlogPostAdmin(AdminWysihtml5TextFieldMixin, admin.ModelAdmin):
    list_display = ('name_en', 'name_fr', 'state', )
    list_filter = ('state', )
    prepopulated_fields = {'slug': ('name_en',)}
    search_fields = ['name_en', 'description_en']
    inlines = [AttachmentInlines]

    class Media:
        js = (
            "/media/js/customHtmlEditor.js",
        )

admin.site.register(BlogPost, BlogPostAdmin)
