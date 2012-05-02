from models import MenusManager
from yacore.decorators import check_api_key
from django.http import Http404, HttpResponse
import json

@check_api_key(methods=['GET'])
def menu_description(request):
    mm = MenusManager()
    groups = list(request.user.groups.values_list('id', flat=True))
    language = request.LANGUAGE_CODE
    app_id = request.app_id
    app_version = request.app_version
    menu = mm.get_menu(language, groups, app_id=app_id, app_version=app_version)
    
    if menu == None:
        return Http404()
    
    sections = menu['sections']
    if not sections:
        return Http404()
    
    res = json.dumps(sections)
    return HttpResponse(res)
    
