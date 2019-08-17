import sys
import requests
import random

from helpers.configurationhelpers import get_host, get_port
from helpers.py2specials import *
from helpers.py3specials import *


url = 'http://{host}:{port}/spellbook/triggers/PaymentProcessorNewPayment/post'.format(host=get_host(), port=get_port())
data = {'seller_id': 'company1',
        'amount_fiat': round(number=random.random() * 100, ndigits=2),
        'currency': 'EUR',
        'note': 'This is a test'}

print('Making new Payment request')
try:
    r = requests.post(url, json=data)
    print(r.text)
except Exception as ex:
    print_to_stderr('POST %s failed: %s' % (url, ex))
    sys.exit(1)
