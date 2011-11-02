from django.contrib import admin
from wall.models import Post

class PostAdmin(admin.ModelAdmin):
  list_display = ('author', 'date', 'data')
  search_fields = ('author', 'data')
  list_filter = ('author', 'date')
    
admin.site.register(Post, PostAdmin)
