import sys
import requests

from helpers.configurationhelpers import get_host, get_port
from helpers.py2specials import *
from helpers.py3specials import *

url = 'http://{host}:{port}/spellbook/triggers/Notary-request/post'.format(host=get_host(), port=get_port())
data = {'message': 'This is a test message2'}

print('Making new Notary request')
try:
    r = requests.post(url, json=data)
    print(r.text)
except Exception as ex:
    print_to_stderr('POST %s failed: %s' % (url, ex))
    sys.exit(1)
