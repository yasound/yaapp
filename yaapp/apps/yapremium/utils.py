from django.conf import settings
import json
import base64
import urllib2

def verifiy_receipt(receipt):
    """
    verify receipt on apple server
    """
    receipt_data = base64.b64encode(receipt)
    json_data = json.dumps({'receipt-data': receipt_data})

    try:
        r = requests.post(settings.APPLE_VERIFY_RECEIPT_URL, data=json_data)
        response = r.json
        if r.status_code == 200 and response.get('status') == 0:
            return True
    except:
        return False
    return False