from models import GeoFeature
import settings as yageoperm_settings

def can_login(user, country):
    if user.is_superuser:
        return True
    
    count = GeoFeature.objects.filter(feature=yageoperm_settings.FEATURE_LOGIN, country__code=country).count()
    if count > 0:
        return True
    return False

def can_create_radio(user, country):
    if user.is_superuser:
        return True
    
    count = GeoFeature.objects.filter(feature=yageoperm_settings.FEATURE_CREATE_RADIO, country__code=country).count()
    if count > 0:
        return True
    return False
    