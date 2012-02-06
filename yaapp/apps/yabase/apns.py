"""
Wrappers for the pyapns client to simplify sending APNS
notifications, including support for re-configuring the
pyapns daemon after a restart.
"""

import pyapns.client
import time
import logging

#log = logging.getLogger('APNS')

def notify(apns_token, message, badge=None, sound=None):
    """Push notification to device with the given message

    @param apns_token - The device's APNS-issued unique token
    @param message - The message to display in the
                     notification window
    """
    notification = {'aps': {'alert': message}}
    if badge is not None:
        notification['aps']['badge'] = int(badge)
    if sound is not None:
        notification['aps']['sound'] = str(sound)
    for attempt in range(4):
        try:
            pyapns.client.notify('MyAppId', apns_token,
                                 notification)
            break
        except (pyapns.client.UnknownAppID,
                pyapns.client.APNSNotConfigured):
            # This can happen if the pyapns server has been
            # restarted since django started running.  In
            # that case, we need to clear the client's
            # configured flag so we can reconfigure it from
            # our settings.py PYAPNS_CONFIG settings.
            if attempt == 3:
                logging.exception('%s', 'unable to send apns notification')
            logging.warning('%s', 'pyapns not configured yet')
            pyapns.client.OPTIONS['CONFIGURED'] = False
            pyapns.client.configure({})
            time.sleep(0.5)

def test():
    notify('aef2f0422172bb9776891a9efddfdd8d8cb73cc29e9582d68c49365df534b2dd', {'aps':{'alert': 'Hello!'}})


