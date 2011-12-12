from tastypie import fields
from tastypie.resources import ModelResource
from models import UserProfile
from django.contrib.auth.models import User
from django.conf.urls.defaults import url
from django.shortcuts import get_object_or_404
from tastypie.utils import trailing_slash
import datetime
from tastypie.authentication import Authentication
from tastypie.authorization import Authorization

class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        fields = ['id', 'username', 'first_name', 'last_name']
        include_resource_uri = False

    def dehydrate(self, bundle):
        userID = bundle.data['id'];
        
        picture = User.objects.get(pk=userID).userprofile.picture
        picture = 'media/' + unicode(picture)
        bundle.data['picture'] = picture
        
        return bundle
