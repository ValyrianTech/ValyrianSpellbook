#!/usr/bin/env python
import sys

import requests
import simplejson

from helpers.configurationhelpers import get_host, get_port
from helpers.setupscripthelpers import clean_up_triggers, spellbook_call

print('Starting Spellbook integration test: HTTP POST request trigger conditions')
print('----------------------------------------------\n')

# Clean up triggers if necessary
clean_up_triggers(trigger_ids=['test_trigger_conditions_HTTPPostRequest_Trigger'])

#########################################################################################################
# HTTP POST request trigger
#########################################################################################################
trigger_id = 'test_trigger_conditions_HTTPPostRequest_Trigger'
trigger_type = 'HTTPPostRequest'
script = 'Echo.py'

# -------------------------------------------------------------------------------------------------

print('Creating HTTP POST request trigger')
response = spellbook_call('save_trigger', trigger_id, f'-t={trigger_type}', f'-sc={script}', '--reset', '--multi')
assert response is None

print('Checking if trigger has not been triggered yet')
response = spellbook_call('get_trigger_config', trigger_id)
assert response['triggered'] == 0
assert response['trigger_type'] == trigger_type

print('Activating HTTP POST request trigger with data')
host, port = get_host(), get_port()
url = f'http://{host}:{port}/spellbook/triggers/{trigger_id}/post'
headers: dict[str, str] = {}
data = {'test': 'hello'}

try:
    r = requests.post(url, headers=headers, json=data)
    print(r.text)
    assert simplejson.loads(r.text) == data
except (ValueError, KeyError, TypeError, OSError) as ex:
    print(f'POST {url} failed: {ex}', file=sys.stderr)
    sys.exit(1)


print('Checking if trigger has been triggered')
response = spellbook_call('get_trigger_config', trigger_id)
assert response['triggered'] > 0

print('Activating HTTP POST request trigger without data')
try:
    r = requests.post(url)
    print(r.text)
    assert r.text == ''
except (ValueError, KeyError, TypeError, OSError) as ex:
    print(f'POST {url} failed: {ex}', file=sys.stderr)
    sys.exit(1)
