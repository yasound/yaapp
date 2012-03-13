from yabase.models import Radio


def my_radios(request):
    if not request.user.is_authenticated():
        return []
    
    radios = Radio.objects.filter(creator=request.user, ready=True)
    return {
        'my_radios': radios
    }