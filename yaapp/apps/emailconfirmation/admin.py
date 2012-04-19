from django.contrib import admin
from models import EmailAddress, EmailConfirmation
from models import EmailTemplate

admin.site.register(EmailAddress)
admin.site.register(EmailConfirmation)

class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ('id', 'email_type', 'subject', 'activated')
    list_editable = ('activated',)
admin.site.register(EmailTemplate, EmailTemplateAdmin)
