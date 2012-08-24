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
        s = urllib2.urlopen(settings.APPLE_VERIFY_RECEIPT_URL, json_data)
        response_data = s.read()
        s.close()

        response_json = json.loads(response_data)
        status = response_json.get('status', '')
    except:
        return False

    if response_data.status == 200 and status == 0:
        return True
    return False
