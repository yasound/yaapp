from django.contrib import admin
from models import Invitation

class InvitationAdmin(admin.ModelAdmin):
    list_display = ('email', 'fullname', 'radio', 'user', 'sent' )
    search_fields = ( 'email', 'user__username', 'radio__name')
admin.site.register(Invitation, InvitationAdmin)

