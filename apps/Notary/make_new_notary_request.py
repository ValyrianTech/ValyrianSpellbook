import sys
import requests

from helpers.configurationhelpers import get_host, get_port
from helpers.http_helpers import DEFAULT_HTTP_TIMEOUT

url = 'http://{host}:{port}/spellbook/triggers/Notary-request/post'.format(host=get_host(), port=get_port())
data = {'message': 'This is a test message2'}

print('Making new Notary request')
try:
    r = requests.post(url, json=data, timeout=DEFAULT_HTTP_TIMEOUT)
    print(r.text)
except Exception as ex:
    print('POST %s failed: %s' % (url, ex), file=sys.stderr)
    sys.exit(1)
