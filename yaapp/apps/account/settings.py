from django.utils.translation import ugettext_lazy as _

ACCOUNT_TYPE_YASOUND = 'yasound'
ACCOUNT_TYPE_FACEBOOK = 'facebook'
ACCOUNT_TYPE_TWITTER = 'twitter'

SUBSCRIPTION_NONE = 'none'
SUBSCRIPTION_PREMIUM = 'premium'

GROUP_NAME_VIP = 'vip'

IOS_TOKEN_TYPE_SANDBOX = 'sandbox'
IOS_TOKEN_TYPE_DEVELOPMENT = 'development'

IOS_TOKEN_TYPE_CHOICES = (
                (IOS_TOKEN_TYPE_SANDBOX, _('Sandbox')),
                (IOS_TOKEN_TYPE_DEVELOPMENT, _('Development'))
                )