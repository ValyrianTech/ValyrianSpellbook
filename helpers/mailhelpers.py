#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

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


def sendmail(recipients, subject, body_template, variables=None, images=None):
    """
    Send an email using the smtp settings in the spellbook.conf file

    :param recipients: Email address(es) of the recipient(s) separated by comma
    :param subject: The subject for the email
    :param body_template: The filename of the body template for the email without the extension (both txt and html versions will be searched for)
    :param variables: A dict containing the variables that will be replaced in the email body template
                      The body template can contain variables like $MYVARIABLE$, if the dict contains a key MYVARIABLE (without $), then it will be replaced by the value of that key
    :param images: A dict containing the filename of the images that need to be embedded in the html email
    :return: True upon success, False upon failure
    """
    if get_enable_smtp() is False:
        LOG.warning('SMTP is disabled, mail will not be sent! see spellbook configuration file')
        return True  # Return true here so everything continues as normal

    # Load the smtp settings
    load_smtp_settings()

    if variables is None:
        variables = {}

    if images is None:
        images = {}

    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = FROM_ADDRESS
    msg['To'] = recipients.replace(',', ', ')

    html_template_filename = None
    txt_template_filename = None
    # Search the 'email-templates' and 'apps' directory for the template
    if os.path.isfile(os.path.join(TEMPLATE_DIR, '%s.html' % body_template)):  # First see if a html template is found in the main template directory
        html_template_filename = os.path.join(TEMPLATE_DIR, '%s.html' % body_template)
    elif os.path.isfile(os.path.join(APPS_DIR, '%s.html' % body_template)):  # Check the app directory for a html template
        html_template_filename = os.path.join(APPS_DIR, '%s.html' % body_template)

    if os.path.isfile(os.path.join(TEMPLATE_DIR, '%s.txt' % body_template)):  # Then check if a txt template if found in the main template directory
        txt_template_filename = os.path.join(TEMPLATE_DIR, '%s.txt' % body_template)
    elif os.path.isfile(os.path.join(APPS_DIR, '%s.txt' % body_template)):  # Lastly, check the app directory for a txt template
        txt_template_filename = os.path.join(APPS_DIR, '%s.txt' % body_template)

    if html_template_filename is None and txt_template_filename is None:
        LOG.error('Template %s for email not found!' % body_template)
        return False

    html_body = ''
    if html_template_filename is not None:
        try:
            with open(html_template_filename, 'r')as input_file:
                html_body = input_file.read()
        except Exception as ex:
            LOG.error('Unable to read template %s: %s' % (html_template_filename, ex))
            return False

    txt_body = ''
    if txt_template_filename is not None:
        try:
            with open(txt_template_filename, 'r')as input_file:
                txt_body = input_file.read()
        except Exception as ex:
            LOG.error('Unable to read template %s: %s' % (txt_template_filename, ex))
            return False

    # Replace all placeholder values in the body like $myvariable$ with the correct value
    for variable, value in variables.items():
        html_body = html_body.replace('$%s$' % str(variable), str(value))
        txt_body = txt_body.replace('$%s$' % str(variable), str(value))

    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(txt_body, 'plain')
    part2 = MIMEText(html_body, 'html')

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    if txt_body != '':
        msg.attach(part1)

    if html_body != '':
        msg.attach(part2)

    # Attach all images that are referenced in the html email template
    for image_name, image_file in images.items():
        try:
            fp = open(image_file, 'rb')
            mime_image = MIMEImage(fp.read())
            fp.close()

            # Define the image's ID as referenced in the template
            mime_image.add_header('Content-ID', '<%s>' % image_name)
            mime_image.add_header('content-disposition', 'attachment', filename=image_name)
            msg.attach(mime_image)
        except Exception as ex:
            LOG.error('Unable to add image %s to email: %s' % (image_name, ex))

    # Attempt to connect to the smtp server and send the message.
    try:
        # Start the smtp session
        session = smtplib.SMTP(HOST, PORT)
        session.ehlo()
        session.starttls()
        session.ehlo()
        session.login(USER, PASSWORD)

        # Send the message and quit
        session.sendmail(FROM_ADDRESS, recipients.split(','), msg.as_string())
        session.quit()

        LOG.info('Email sent to %s : %s (template: %s)' % (recipients.split(','), subject, body_template))
        return True

    except Exception as ex:
        LOG.error('Failed sending mail: %s' % ex)
        return False
