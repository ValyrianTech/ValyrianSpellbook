#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import smtplib

from helpers.loghelpers import LOG
from helpers.configurationhelpers import get_smtp_from_address, get_smtp_host, get_smtp_port, get_smtp_user, get_smtp_password


FROM_ADDRESS = ''
HOST = ''
PORT = 25
USER = ''
PASSWORD = ''

TEMPLATE_DIR = 'email_templates'


def load_smtp_settings():
    global FROM_ADDRESS, HOST, PORT, USER, PASSWORD
    FROM_ADDRESS = get_smtp_from_address()
    HOST = get_smtp_host()
    PORT = get_smtp_port()
    USER = get_smtp_user()
    PASSWORD = get_smtp_password()


def sendmail(recipients, subject, body_template, variables=None):
    """
    Send an email using the smtp settings in the Spellbook.conf file

    :param recipients: Email address(es) of the recipient(s) separated by semicolon
    :param subject: The subject for the email
    :param body_template: The filename of the body template for the email
    :param variables: A dict containing the variables that will be replaced in the email body template
                      The body template can contain variables like #MYVARIABLE#, if the dict contains a key MYVARIABLE (without #), then it will be replaced by the value of that key
    :return: True upon success, False upon failure
    """
    if variables is None:
        variables = {}

    # Load the smtp settings
    load_smtp_settings()

    # Set the message headers in a list.
    headers = [
        "From: %s" % FROM_ADDRESS,
        "To: %s" % recipients,
        "Subject: %s" % subject,
        "Content-Type: text/plain"
    ]

    try:
        with open(os.path.join(TEMPLATE_DIR, '%s.txt' % body_template), 'r') as input_file:
            body = input_file.read()
    except IOError:
        LOG.error('Template for email not found: %s' % body_template)
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
        session.sendmail(FROM_ADDRESS, recipients.split(';'), "\r\n".join(headers) + "\r\n\r\n" + body)
        session.quit()

        LOG.info('Email sent to %s : %s (template: %s)' % (recipients, subject, body_template))
        return True

    except Exception as ex:
        LOG.error('Failed sending mail: %s' % ex)
        return False
