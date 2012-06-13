from django.contrib import admin
from models import UserProfile, Device 
from sorl.thumbnail.admin import AdminImageMixin

class UserProfileAdmin(AdminImageMixin, admin.ModelAdmin):
    list_display = ('id', 'user', 'name', 'twitter_uid', 'facebook_uid')
    search_fields = ['user__username',]
    exclude = ('notifications_preferences',)
    def make_mailing_list(self, request, queryset):
        from emencia.django.newsletter.models import Contact
        from emencia.django.newsletter.models import MailingList
        
        subscribers = []
        for profile in queryset:
            email = profile.user.email
            first_name = ''
            last_name = profile.name
            if email is not None:
                contact, _created = Contact.objects.get_or_create(email=email,
                                                                 defaults={'first_name': first_name,
                                                                           'last_name': last_name,
                                                                           'content_object': profile})
                subscribers.append(contact)
        mailing, _created = MailingList.objects.get_or_create(name='all',
                                  defaults={'description': 'All users'})
        mailing.subscribers.add(*subscribers)
        self.message_user(request, '%s succesfully created.' % mailing)
    make_mailing_list.short_description = 'Add users to mailing list contact list'

    actions = ['make_mailing_list']
        
admin.site.register(UserProfile, UserProfileAdmin)

class DeviceAdmin(admin.ModelAdmin):
    list_display = ('user', 'ios_token')
    search_fields = ['user__username', 'ios_token']
admin.site.register(Device, DeviceAdmin)
    
