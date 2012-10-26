from django.contrib import admin
from models import EmailAddress, EmailConfirmation
from models import EmailTemplate

class EmailAddressAdmin(admin.ModelAdmin):
    list_display = ('email', 'user', 'verified', 'primary')
    list_filter = ('verified',)
admin.site.register(EmailAddress, EmailAddressAdmin)

class EmailConfirmationAdmin(admin.ModelAdmin):
    list_display = ('email_address', 'sent', 'confirmation_key', 'retries')
admin.site.register(EmailConfirmation, EmailConfirmationAdmin)

class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ('id', 'email_type', 'subject', 'activated')
    list_editable = ('activated',)
admin.site.register(EmailTemplate, EmailTemplateAdmin)
