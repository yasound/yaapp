from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from models import User, UserProfile
import datetime

PICTURE_FILE_TAG = 'picture'

@csrf_exempt
def set_user_picture(request, user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return HttpResponse('user does not exist')
    
    if not request.FILES.has_key(PICTURE_FILE_TAG):
        return HttpResponse('request does not contain a picture file')
    
    f = request.FILES[PICTURE_FILE_TAG]
    d = datetime.datetime.now()
    filename = unicode(d) + '.png'
    
    user.userprofile.picture.save(filename, f)
    
    res = 'picture OK for user: %s' % unicode(user)
    return HttpResponse(res)
    