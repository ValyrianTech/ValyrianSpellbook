import sys
import requests

from helpers.configurationhelpers import get_host, get_port
from helpers.py2specials import *
from helpers.py3specials import *

payment_request_id = input("Enter the payment-request-id")
url = 'http://{host}:{port}/spellbook/triggers/PaymentProcessorPaymentStatus/get'.format(host=get_host(), port=get_port())
data = {'payment_request_id': payment_request_id}

print 'Checking status of Payment Request %s' % payment_request_id
try:
    r = requests.get(url, json=data)
    print(r.text)
except Exception as ex:
    print_to_stderr('GET %s failed: %s' % (url, ex))
    sys.exit(1)
