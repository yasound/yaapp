# From : http://leecutsco.de/2009/07/14/push-on-the-iphone/
from django.db import models
from django.conf import settings
 
from socket import socket
 
import datetime
import struct
import ssl
import binascii
import json
 
def send_message(udid, alert, badge=0, sound="chime", sandbox=True,
                        custom_params={}, action_loc_key=None, loc_key=None,
                        loc_args=[], passed_socket=None):
        """
        Send a message to an iPhone using the APN server, returns whether
        it was successful or not.
 
        alert - The message you want to send
        badge - Numeric badge number you wish to show, 0 will clear it
        sound - chime is shorter than default! Replace with None/"" for no sound
        sandbox - Are you sending to the sandbox or the live server
        custom_params - A dict of custom params you want to send
        action_loc_key - As per APN docs
        loc_key - As per APN docs
        loc_args - As per APN docs, make sure you use a list
        passed_socket - Rather than open/close a socket, use an already open one
 
        This requires IPHONE_APN_PUSH_CERT in settings.py to be the full
        path to the cert/pk .pem file.
        """
        aps_payload = {}
 
        alert_payload = alert
        if action_loc_key or loc_key or loc_args:
            alert_payload = {'body' : alert}
            if action_loc_key:
                alert_payload['action-loc-key'] = action_loc_key
            if loc_key:
                alert_payload['loc-key'] = loc_key
            if loc_args:
                alert_payload['loc-args'] = loc_args
 
        aps_payload['alert'] = alert_payload
 
        if badge:
            aps_payload['badge'] = badge
 
        if sound:
            aps_payload['sound'] = sound        
 
        payload = custom_params
        payload['aps'] = aps_payload
 
        s_payload = json.dumps(payload, separators=(',',':'))
 
        fmt = "!cH32sH%ds" % len(s_payload)
        command = '\x00'
        msg = struct.pack(fmt, command, 32, binascii.unhexlify(udid), len(s_payload), s_payload)
 
        if passed_socket:
            passed_socket.write(msg)
        else:
            host_name = 'gateway.sandbox.push.apple.com' if sandbox else 'gateway.push.apple.com'
            s = socket()
            c = ssl.wrap_socket(s,
                                ssl_version=ssl.PROTOCOL_SSLv3,
                                certfile=settings.IPHONE_APN_PUSH_CERT)
            c.connect((host_name, 2195))
            c.write(msg)
            c.close()
 
        return True
 


def test():
# aef2f0422172bb9776891a9efddfdd8d8cb73cc29e9582d68c49365df534b2dd
    send_message('aef2f0422172bb9776891a9efddfdd8d8cb73cc29e9582d68c49365df534b2dd', 'Hello!', sandbox=True)
    #host_name = 'gateway.sandbox.push.apple.com'
    #s = socket()
    #c = ssl.wrap_socket(s,
    #                    ssl_version=ssl.PROTOCOL_SSLv3,
    #                    certfile=settings.IPHONE_APN_PUSH_CERT)
    #c.connect((host_name, 2195))
    ##c.write(msg)
    #send_message('aef2f0422172bb9776891a9efddfdd8d8cb73cc29e9582d68c49365df534b2dd', 'Hello!', sandbox=True, passed_socket=c)
    #send_message('aef2f0422172bb9776891a9efddfdd8d8cb73cc29e9582d68c49365df534b2dd', 'Bleh!', sandbox=True, passed_socket=c)
    #c.close()


