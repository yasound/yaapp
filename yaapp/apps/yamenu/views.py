from models import MenusManager
from yacore.decorators import check_api_key
from django.http import Http404, HttpResponse
import json

@check_api_key(methods=['GET'])
def menu_description(request):
    mm = MenusManager()
    name = 'default'
    language = request.LANGUAGE_CODE
    menu = mm.get_menu(name, language)
    if menu == None:
        language = 'en'
        menu = mm.get_menu(name, language)
    sections = mm['sections']
    if not sections:
        return Http404()
    
    res = json.dumps(sections)
    return HttpResponse(res)
    
