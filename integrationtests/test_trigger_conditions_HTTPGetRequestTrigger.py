#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import requests
import simplejson

from integration_test_helpers import spellbook_call
from helpers.configurationhelpers import get_host, get_port


# Change working dir up one level
os.chdir("..")

print 'Starting Spellbook integration test: HTTP GET request trigger conditions'
print '----------------------------------------------\n'

#########################################################################################################
# HTTP GET request trigger
#########################################################################################################

print 'Getting the list of configured triggers'
configured_triggers = spellbook_call('get_triggers')

trigger_id = 'test_trigger_conditions_HTTPGetRequest_Trigger'

# Clean up old test action if necessary
if trigger_id in configured_triggers:
    response = spellbook_call('delete_trigger', trigger_id)
    assert response is None

# --------------------------------------------------------------------------------------------------------
trigger_type = 'HTTPGetRequest'
script = 'Echo'
# -------------------------------------------------------------------------------------------------
print 'Creating HTTP GET request trigger'
response = spellbook_call('save_trigger', trigger_id, '-t=%s' % trigger_type, '-sc=%s' % script, '--reset', '--multi')
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