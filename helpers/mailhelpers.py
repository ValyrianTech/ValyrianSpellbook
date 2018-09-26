#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import smtplib

from helpers.loghelpers import LOG
from helpers.configurationhelpers import get_smtp_from_address, get_smtp_host, get_smtp_port, get_smtp_user, get_smtp_password
from helpers.configurationhelpers import get_enable_smtp


FROM_ADDRESS = ''
HOST = ''
PORT = 25
USER = ''
PASSWORD = ''

PROGRAM_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TEMPLATE_DIR = os.path.join(PROGRAM_DIR, 'email_templates')
APPS_DIR = os.path.join(PROGRAM_DIR, 'apps')


def load_smtp_settings():
    global FROM_ADDRESS, HOST, PORT, USER, PASSWORD
    FROM_ADDRESS = get_smtp_from_address()
    HOST = get_smtp_host()
    PORT = get_smtp_port()
    USER = get_smtp_user()
    PASSWORD = get_smtp_password()


def sendmail(recipients, subject, body_template, variables=None):
    """
    Send an email using the smtp settings in the spellbook.conf file

    :param recipients: Email address(es) of the recipient(s) separated by comma
    :param subject: The subject for the email
    :param body_template: The filename of the body template for the email
    :param variables: A dict containing the variables that will be replaced in the email body template
                      The body template can contain variables like #MYVARIABLE#, if the dict contains a key MYVARIABLE (without #), then it will be replaced by the value of that key
    :return: True upon success, False upon failure
    """
    if variables is None:
        variables = {}

    if get_enable_smtp() is False:
        LOG.warning('SMTP is disabled, mail will not be sent! see spellbook configuration file')
        return True  # Return true here so everything continues as normal

    # Load the smtp settings
    load_smtp_settings()

    # Set the message headers in a list.
    headers = [
        "From: %s" % FROM_ADDRESS,
        "To: %s" % recipients.replace(',', ', '),  # there needs to be a space in between
        "Subject: %s" % subject,
        "Content-Type: text/plain"
    ]

    # Search the 'email-templates' and 'apps' directory for the template
    if os.path.isfile(os.path.join(TEMPLATE_DIR, body_template)):
        template_filename = os.path.join(TEMPLATE_DIR, body_template)
    elif os.path.isfile(os.path.join(APPS_DIR, body_template)):
        template_filename = os.path.join(APPS_DIR, body_template)
    else:
        LOG.error('Template %s for email not found!' % body_template)
        return False

    try:
        with open(template_filename, 'r')as input_file:
            body = input_file.read()
    except Exception as ex:
        LOG.error('Unable to read template %s: %s' % (template_filename, ex))
        return False

    # Replace all placeholder values in the body like $myvariable$ with the correct value
    for variable, value in variables.items():
        body = body.replace('$%s$' % str(variable), str(value))

    # Attempt to connect to the smtp server and send the message.
    try:
        # Start the smtp session
        session = smtplib.SMTP(HOST, PORT)
        session.ehlo()
        session.starttls()
        session.ehlo()
        session.login(USER, PASSWORD)

        # Send the message and quit
        session.sendmail(FROM_ADDRESS, recipients.split(','), "\r\n".join(headers) + "\r\n\r\n" + body)
        session.quit()

        LOG.info('Email sent to %s : %s (template: %s)' % (recipients.split(','), subject, body_template))
        return True

    except Exception as ex:
        LOG.error('Failed sending mail: %s' % ex)
        return False
