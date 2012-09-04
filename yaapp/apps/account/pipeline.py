from account.api import build_random_username
from account.models import UserProfile
from django.contrib.auth.models import User
import settings as account_settings

def associate_user(backend, details, response, uid, username, user=None, *args,
                **kwargs):
    """
    this is called by the social auth pipeline when user creation is needed.
    We hack it to associate with existing users (by checking the profile fields)
    or create new but with our profile info inside
    """
    backend_name = backend.name.lower()

    # existing user
    if user:
        if backend_name == 'facebook':
            profile = user.get_profile()
            if profile and not profile.facebook_enabled:
                profile.facebook_uid = uid
                profile.add_account_type(account_settings.ACCOUNT_MULT_FACEBOOK)
                profile.save()
        elif backend_name == 'twitter':
            profile = user.get_profile()
            if profile and not profile.twitter_enabled:
                profile.twitter_uid = uid
                profile.add_account_type(account_settings.ACCOUNT_MULT_TWITTER)
                profile.save()

        try:
            profile.scan_friends()
        except:
            pass
        try:
            if not profile.picture:
                profile.update_with_social_picture()
        except:
            pass

        try:
            profile.logged()
        except:
            pass

        return {'user': user}
    if not username:
        return None

    # new user
    if backend_name == 'facebook':
        try:
            profile = UserProfile.objects.get(facebook_uid=uid)
            user = profile.user
            return {'user': user}
        except UserProfile.DoesNotExist:
            user = User.objects.create_user(username=build_random_username(), email=details.get('email'))
            user.first_name = details.get('first_name')
            user.last_name = details.get('last_name')
            user.save()
            profile = user.get_profile()
            profile.facebook_uid = uid
            profile.name = details.get('fullname')
            profile.add_account_type(account_settings.ACCOUNT_MULT_FACEBOOK)
            try:
                profile.scan_friends()
            except:
                pass
            try:
                if not profile.picture:
                    profile.update_with_social_picture()
            except:
                pass

            return {
                'user': user,
                'is_new': True
            }
    elif backend_name == 'twitter':
        try:
            profile = UserProfile.objects.get(twitter_uid=uid)
            user = profile.user
            return {'user': user}
        except UserProfile.DoesNotExist:
            user = User.objects.create_user(username=build_random_username(), email=details.get('email'))
            user.first_name = details.get('first_name')
            user.last_name = details.get('last_name')
            user.save()
            profile = user.get_profile()
            profile.twitter_uid = uid
            profile.name = details.get('fullname')
            profile.add_account_type(account_settings.ACCOUNT_MULT_TWITTER)
            try:
                profile.scan_friends()
            except:
                pass
            try:
                if profile.picture is None:
                    profile.update_with_social_picture()
            except:
                pass
            
            try:
                profile.logged()
            except:
                pass

            return {
                'user': user,
                'is_new': True
            }

