import sys
import requests
import random

from helpers.configurationhelpers import get_host, get_port


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
    print('POST %s failed: %s' % (url, ex), file=sys.stderr)
    sys.exit(1)
