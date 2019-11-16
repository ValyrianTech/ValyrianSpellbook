#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import requests
import simplejson

from helpers.setupscripthelpers import spellbook_call, clean_up_triggers
from helpers.configurationhelpers import get_host, get_port


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
response = spellbook_call('save_trigger', trigger_id, '-t=%s' % trigger_type, '-sc=%s' % script, '--reset', '--multi')
assert response is None

print('Checking if trigger has not been triggered yet')
response = spellbook_call('get_trigger_config', trigger_id)
assert response['triggered'] is 0
assert response['trigger_type'] == trigger_type

print('Activating HTTP POST request trigger with data')
host, port = get_host(), get_port()
url = 'http://{host}:{port}/spellbook/triggers/{trigger_id}/post'.format(host=host, port=port, trigger_id=trigger_id)
headers = {}
data = {'test': 'hello'}

try:
    r = requests.post(url, headers=headers, json=data)
    print(r.text)
    assert simplejson.loads(r.text) == data
except Exception as ex:
    print('POST %s failed: %s' % (url, ex), file=sys.stderr)
    sys.exit(1)


print('Checking if trigger has been triggered')
response = spellbook_call('get_trigger_config', trigger_id)
assert response['triggered'] > 0

print('Activating HTTP POST request trigger without data')
try:
    r = requests.post(url)
    print(r.text)
    assert r.text == ''
except Exception as ex:
    print('POST %s failed: %s' % (url, ex), file=sys.stderr)
    sys.exit(1)
