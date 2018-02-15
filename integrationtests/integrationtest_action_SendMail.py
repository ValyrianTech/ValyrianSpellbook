#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from integration_test_helpers import spellbook_call

# Change working dir up one level
os.chdir("..")

print 'Starting Spellbook integration test: SendMail actions'
print '----------------------------------------------\n'

#########################################################################################################
# SendMail actions
#########################################################################################################

print 'Getting the list of configured actions'
configured_triggers = spellbook_call('get_actions')

action_name = 'integrationtest_action_SendMail'

# Clean up old test action if necessary
if action_name in configured_triggers:
    response = spellbook_call('delete_action', action_name)
    assert response is None

# --------------------------------------------------------------------------------------------------------
mail_recipients = 'info@valyrian.tech'
mail_subject = 'example email subject'
mail_body_template = 'template1'

print 'Creating test action: SendMailAction'
response = spellbook_call('save_action', '-t=SendMail', action_name, '-mr=%s' % mail_recipients, '-ms=%s' % mail_subject, "-mb=%s" % mail_body_template)
assert response is None

# --------------------------------------------------------------------------------------------------------
print 'Getting the list of configured action_ids'
response = spellbook_call('get_actions')
assert action_name in response

# --------------------------------------------------------------------------------------------------------
print 'Getting the action config of the action we just created'
response = spellbook_call('get_action_config', action_name)
assert response['id'] == action_name
assert response['action_type'] == 'SendMail'
assert response['mail_recipients'] == mail_recipients
assert response['mail_subject'] == mail_subject
assert response['mail_body_template'] == mail_body_template

# --------------------------------------------------------------------------------------------------------
# uncomment following lines to actually send the email
# print 'Running the action we just created'
# response = spellbook_call('run_action', action_name)
# assert response is True
