#!/usr/bin/env python
# -*- coding: utf-8 -*-
import qrcode
import io

from helpers.loghelpers import LOG


def generate_qr(message, border=4, box_size=64, error='M', version=None):
    """
    Generate a QR code image

    :param message: String - the message to encode as a QR code
    :param border: integer - Size of the border
    :param box_size: integer - size of the box
    :param error: String - Error correction level ('L', 'M', 'Q', 'H')
    :param version: Integer - Set to None for auto-fit, or a value from 1 to 40

    :return: the QR code bytes
    """
    LOG.info('Generating QR code image for: %s' % message)

    if error not in ['L', 'M', 'Q', 'H']:
        LOG.error('Invalid error correction value: %s' % error)
        error_correction = 'M'

    else:
        if error == 'L':
            error_correction = qrcode.constants.ERROR_CORRECT_L
        elif error == 'M':
            error_correction = qrcode.constants.ERROR_CORRECT_M
        elif error == 'Q':
            error_correction = qrcode.constants.ERROR_CORRECT_Q
        elif error == 'H':
            error_correction = qrcode.constants.ERROR_CORRECT_H
        else:
            raise NotImplementedError('Unknown error correction type: %s' % error)

    qr = qrcode.QRCode(
        version=version,
        error_correction=error_correction,
        box_size=box_size,
        border=border,
    )
    qr.add_data(message)
    qr.make(fit=True)

    image = qr.make_image()

    image_byte_array = io.BytesIO()
    image.save(image_byte_array, format=image.format)
    image_byte_array = image_byte_array.getvalue()

    return image_byte_array
