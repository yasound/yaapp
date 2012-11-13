from django.conf import settings
import json
import base64
import requests
import logging
import string
import random
from datetime import *
from dateutil.relativedelta import *
import settings as yapremium_settings
logger = logging.getLogger("yaapp.yapremium")


def verify_receipt(receipt, encode=False):
    """
    verify receipt on apple server
    """
    if encode:
        receipt_data = base64.b64encode(receipt)
    else:
        receipt_data = receipt

    json_data = json.dumps({'receipt-data': receipt_data})
    r = requests.post(settings.APPLE_VERIFY_RECEIPT_URL, data=json_data, verify=False)
    logger.debug(r.raw)
    logger.debug(r.status_code)
    response = r.json
    logger.debug(response)
    if r.status_code == 200 and response.get('status') == 0:
        return True

    return False


def calculate_expiration_date(duration, duration_unit, today=None):
    if not today:
        today = date.today()

    if duration_unit == yapremium_settings.DURATION_DAY:
        return today + relativedelta(days=+duration)
    elif duration_unit == yapremium_settings.DURATION_WEEK:
        return today + relativedelta(weeks=+duration)
    elif duration_unit == yapremium_settings.DURATION_MONTH:
        return today + relativedelta(months=+duration)
    return today


def generate_code_name(prefix=''):
    from models import Promocode
    code_length = 6
    suffix = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(code_length))
    code_name = prefix + suffix
    while Promocode.objects.filter(code=code_name).count() > 0:
        suffix = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(code_length))
        code_name = prefix + suffix
    return code_name
