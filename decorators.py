#!/usr/bin/python
# -*- coding: utf-8 -*-

import simplejson
from bottle import request
from authentication import check_authentication, AuthenticationStatus
from data.data import set_explorer, clear_explorer, EXPLORER


def authentication_required(f):
    """
    Decorator to check authentication before allowing access to certain functions

    :param f: The function that requires authentication
    :return: The result of the function OR a json dict containing the reason of the authentication failure
    """

    def decorated_function(*args, **kwargs):
        authentication_status = check_authentication(request.headers, request.json)
        if authentication_status == AuthenticationStatus.OK:
            return f(*args, **kwargs)
        else:
            return simplejson.dumps({'error': authentication_status})
    return decorated_function


def use_explorer(f):
    """
    Decorator that sets the specified explorer (if one is given) as a global variable before a request is executed
    and sets the global variable back to None at the end

    :param f: The function that requires authentication
    :return: The result of the function
    """

    def decorated_function(*args, **kwargs):
        if request.query.explorer != '':
            set_explorer(request.query.explorer)

        ret = f(*args, **kwargs)
        if isinstance(ret, dict):
            ret['explorer'] = EXPLORER

        clear_explorer()
        return ret

    return decorated_function
