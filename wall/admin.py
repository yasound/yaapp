from django.contrib import admin
from wall.models import Post

class PostAdmin(admin.ModelAdmin):
  list_display = ('author', 'date', 'post')
  search_fields = ('author', 'post')
  list_filter = ('author', 'date')
    
admin.site.register(Post, PostAdmin)
