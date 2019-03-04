import sys
import requests

from helpers.configurationhelpers import get_host, get_port
from helpers.hotwallethelpers import get_address_from_wallet

voucher = 'ABC123'
address = get_address_from_wallet(account=0, index=1)

url = 'http://{host}:{port}/api/RedeemVoucher'.format(host=get_host(), port=get_port())
data = {'voucher': voucher, 'address': address}

print 'Making new Voucher request'
try:
    r = requests.post(url, json=data)
    print r.text
except Exception as ex:
    print >> sys.stderr, 'POST %s failed: %s' % (url, ex)
    sys.exit(1)
