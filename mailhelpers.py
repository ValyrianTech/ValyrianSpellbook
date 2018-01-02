import os
import smtplib
import logging
from ConfigParser import ConfigParser


FROM_ADDRESS = ''
HOST = ''
PORT = 25
USER = ''
PASSWORD = ''

TEMPLATE_DIR = 'email_templates'


def load_smtp_settings():
    global FROM_ADDRESS, HOST, PORT, USER, PASSWORD
    # Read the RESTAPI configuration file
    spellbook_configuration_file = 'configuration/Spellbook.conf'
    config = ConfigParser()
    config.read(spellbook_configuration_file)

    # Check if the spellbook configuration file contains a [SMTP] section
    if not config.has_section('SMTP'):
        raise Exception('Configuration file %s does not have a [SMTP] section ' % spellbook_configuration_file)

    # Check if the [SMTP] section has options for 'from_address'
    if not config.has_option('SMTP', 'from_address'):
        raise Exception("Configuration file %s does not have an option 'from_address' in the [SMTP] section" % spellbook_configuration_file)
    FROM_ADDRESS = config.get('SMTP', 'from_address')

    # Check if the [SMTP] section has options for 'host'
    if not config.has_option('SMTP', 'host'):
        raise Exception("Configuration file %s does not have an option 'host' in the [SMTP] section" % spellbook_configuration_file)
    HOST = config.get('SMTP', 'host')

    # Check if the [SMTP] section has options for 'port'
    if not config.has_option('SMTP', 'port'):
        raise Exception("Configuration file %s does not have an option 'port' in the [SMTP] section" % spellbook_configuration_file)
    PORT = config.get('SMTP', 'port')

    # Check if the [SMTP] section has options for 'user'
    if not config.has_option('SMTP', 'user'):
        raise Exception("Configuration file %s does not have an option 'user' in the [SMTP] section" % spellbook_configuration_file)
    USER = config.get('SMTP', 'user')

    # Check if the [SMTP] section has options for 'password'
    if not config.has_option('SMTP', 'password'):
        raise Exception("Configuration file %s does not have an option 'password' in the [SMTP] section" % spellbook_configuration_file)
    PASSWORD = config.get('SMTP', 'password')


def sendmail(recipients, subject, body_template):
    """
    Send an email using the smtp settings in the Spellbook.conf file

    :param recipients: Email address(es) of the recipient(s) separated by semicolon
    :param subject: The subject for the email
    :param body_template: The filename of the body template for the email
    :return: True upon success, False upon failure
    """
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
        logging.getLogger('Spellbook').error('Template for email not found: %s' % body_template)
        return False

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

        logging.getLogger('Spellbook').info('Email sent to %s : %s (template: %s)' % (recipients, subject, body_template))
        return True

    except Exception as ex:
        logging.getLogger('Spellbook').error('Failed sending mail: %s' % ex)
        return False
