#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import requests
import simplejson

from helpers.setupscripthelpers import spellbook_call, clean_up_triggers
from helpers.configurationhelpers import get_host, get_port


print 'Starting Spellbook integration test: HTTP GET request trigger conditions'
print '----------------------------------------------\n'

# Clean up triggers if necessary
clean_up_triggers(trigger_ids=['test_trigger_conditions_DeadMansSwitchTrigger'])

#########################################################################################################
# HTTP GET request trigger
#########################################################################################################
trigger_id = 'test_trigger_conditions_HTTPGetRequest_Trigger'
trigger_type = 'HTTPGetRequest'
script = 'Echo.py'

# -------------------------------------------------------------------------------------------------

print 'Creating HTTP GET request trigger'
response = spellbook_call('save_trigger', trigger_id, '-t=%s' % trigger_type, '-sc=%s' % script, '-st=Active', '--multi')
assert response is None

print 'Checking if trigger has not been triggered yet'
response = spellbook_call('get_trigger_config', trigger_id)
assert response['triggered'] is 0
assert response['trigger_type'] == trigger_type

print 'Activating HTTP GET request trigger with data'
host, port = get_host(), get_port()
url = 'http://{host}:{port}/spellbook/triggers/{trigger_id}/get'.format(host=host, port=port, trigger_id=trigger_id)
headers = {}
data = {'test': 'hello'}

try:
    r = requests.get(url, headers=headers, json=data)
    print r.text
    assert simplejson.loads(r.text) == data
except Exception as ex:
    print >> sys.stderr, 'GET %s failed: %s' % (url, ex)
    sys.exit(1)


print 'Checking if trigger has been triggered'
response = spellbook_call('get_trigger_config', trigger_id)
assert response['triggered'] > 0

print 'Activating HTTP Get request trigger without data'
try:
    r = requests.get(url)
    print r.text
    assert r.text == ''
except Exception as ex:
    print >> sys.stderr, 'GET %s failed: %s' % (url, ex)
    sys.exit(1)
