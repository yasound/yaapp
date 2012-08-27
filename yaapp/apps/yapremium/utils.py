from django.conf import settings
import json
import base64
import urllib2
import requests
import logging
logger = logging.getLogger("yaapp.yapremium")

def verify_receipt(receipt):
    """
    verify receipt on apple server
    """
    receipt_data = base64.b64encode(receipt)
    json_data = json.dumps({'receipt-data': receipt_data})
    r = requests.post(settings.APPLE_VERIFY_RECEIPT_URL, data=json_data, verify=False)
    logger.debug(r.raw)
    logger.debug(r.status_code)
    response = r.json
    logger.debug(response)
    if r.status_code == 200 and response.get('status') == 0:
        return True

    return False