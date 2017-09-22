#!/usr/bin/python
# -*- coding: utf-8 -*-

import simplejson
from bottle import request
from authentication import check_authentication, AuthenticationStatus


def authentication_required(f):
    """
    Decorator to check authentication before allowing access to certain functions

    :param f: The function that requires authentication
    :return: The result of the function OR a json dict containing the reason of the authentication failure
    """

    def decorated_function(*args, **kwargs):
        authentication_status = check_authentication(request.headers, request.body.getvalue())
        if authentication_status == AuthenticationStatus.OK:
            return f(*args, **kwargs)
        else:
            return simplejson.dumps({'error': authentication_status})
    return decorated_function

