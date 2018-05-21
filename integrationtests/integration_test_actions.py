#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from integration_test_helpers import spellbook_call

# Change working dir up one level
os.chdir("..")

print 'Starting Spellbook integration test: actions'
print '----------------------------------------------\n'

#########################################################################################################
# Command actions
#########################################################################################################

print 'Getting the list of configured actions'
configured_triggers = spellbook_call('get_actions')

action_name = 'test_action_Command'

# Clean up old test action if necessary
if action_name in configured_triggers:
    response = spellbook_call('delete_action', action_name)
    assert response is None

# --------------------------------------------------------------------------------------------------------
run_command = 'ping 127.0.0.1 > integrationtests/ping_output.txt'
print 'Creating test action: CommandAction'
response = spellbook_call('save_action', '-t=Command', action_name, '-c=%s' % run_command)
assert response is None

# --------------------------------------------------------------------------------------------------------
print 'Getting the list of configured action_ids'
response = spellbook_call('get_actions')
assert action_name in response

# --------------------------------------------------------------------------------------------------------
print 'Getting the action config of the action we just created'
response = spellbook_call('get_action_config', action_name)
assert response['id'] == action_name
assert response['action_type'] == 'Command'
assert response['run_command'] == run_command

# --------------------------------------------------------------------------------------------------------
print 'Running the action we just created'
response = spellbook_call('run_action', action_name)
assert response is True


#########################################################################################################
# SendMail actions
#########################################################################################################

print 'Getting the list of configured actions'
configured_triggers = spellbook_call('get_actions')

action_name = 'test_action_SendMail'

# Clean up old test action if necessary
if action_name in configured_triggers:
    response = spellbook_call('delete_action', action_name)
    assert response is None

# --------------------------------------------------------------------------------------------------------
mail_recipients = 'skidzobolder@gmail.com;wouter.glorieux@gmail.com'
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
# print 'Running the action we just created'
# response = spellbook_call('run_action', action_name)
# assert response is True


#########################################################################################################
# Webhook actions
#########################################################################################################

print 'Getting the list of configured actions'
configured_triggers = spellbook_call('get_actions')

action_name = 'test_action_Webhook'

# Clean up old test action if necessary
if action_name in configured_triggers:
    response = spellbook_call('delete_action', action_name)
    assert response is None

# --------------------------------------------------------------------------------------------------------
webhook = 'http://www.google.com'

print 'Creating test action: Webhook'
response = spellbook_call('save_action', '-t=Webhook', action_name, '-w=%s' % webhook)
assert response is None

# --------------------------------------------------------------------------------------------------------
print 'Getting the list of configured action_ids'
response = spellbook_call('get_actions')
assert action_name in response

# --------------------------------------------------------------------------------------------------------
print 'Getting the action config of the action we just created'
response = spellbook_call('get_action_config', action_name)
assert response['id'] == action_name
assert response['action_type'] == 'Webhook'
assert response['webhook'] == webhook

# --------------------------------------------------------------------------------------------------------
print 'Running the action we just created'
response = spellbook_call('run_action', action_name)
assert response is True


#########################################################################################################
# RevealSecret actions
#########################################################################################################

print 'Getting the list of configured actions'
configured_triggers = spellbook_call('get_actions')

action_name = 'test_action_RevealSecret'

# Clean up old test action if necessary
if action_name in configured_triggers:
    response = spellbook_call('delete_action', action_name)
    assert response is None

# --------------------------------------------------------------------------------------------------------
reveal_text = 'A secret message'
reveal_link = 'http://www.asecretlink.com'

print 'Creating test action: RevealSecret'
response = spellbook_call('save_action', '-t=RevealSecret', action_name, '-rt=%s' % reveal_text, '-rl=%s' % reveal_link)
assert response is None

# --------------------------------------------------------------------------------------------------------
print 'Getting the list of configured action_ids'
response = spellbook_call('get_actions')
assert action_name in response

# --------------------------------------------------------------------------------------------------------
print 'Getting the action config of the action we just created'
response = spellbook_call('get_action_config', action_name)
assert response['id'] == action_name
assert response['action_type'] == 'RevealSecret'
assert response['reveal_text'] == reveal_text
assert response['reveal_link'] == reveal_link

# --------------------------------------------------------------------------------------------------------
print 'Checking if reveal is none because action has not been activated yet'
response = spellbook_call('get_reveal', action_name)
assert response is None

# --------------------------------------------------------------------------------------------------------
print 'Activating the action we just created'
response = spellbook_call('run_action', action_name)
assert response is True

# --------------------------------------------------------------------------------------------------------
print 'Checking if reveal is given because action has been activated'
response = spellbook_call('get_reveal', action_name)
assert response['reveal_text'] == reveal_text
assert response['reveal_link'] == reveal_link
