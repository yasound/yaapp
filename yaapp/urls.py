from django.conf.urls.defaults import patterns, include, url
from tastypie.api import Api
from yabase.api import SongMetadataResource, SongInstanceResource, PlaylistResource, UserProfileResource, RadioResource
from yabase.api import RadioEventResource
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

api = Api(api_name='v1')
api.register(SongMetadataResource())
api.register(SongInstanceResource())
api.register(PlaylistResource())
api.register(UserProfileResource())
api.register(RadioEventResource())
api.register(RadioResource())

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'yaapp.views.home', name='home'),
    # url(r'^yaapp/', include('yaapp.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    #(r'^wall/', include('wall.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^wall/', include('wall.urls')),
    (r'^api/', include(api.urls)),
)
