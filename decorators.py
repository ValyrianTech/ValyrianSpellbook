#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Decorators for authentication, explorer selection, JSON output, config verification, and logging."""
import functools
import os
import simplejson
import time
from bottle import request
from configparser import ConfigParser
from functools import wraps

from authentication import check_authentication, AuthenticationStatus
from data.data import set_explorer, clear_explorer, get_last_explorer
from helpers.loghelpers import LOG

CONFIGURATION_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "configuration", "spellbook.conf"))


def authentication_required(f):
    """
    Decorator to check authentication before allowing access to certain functions

    :param f: The function that requires authentication
    :return: The result of the function OR a json dict containing the reason of the authentication failure
    """

    def decorated_function(*args, **kwargs):
        """Execute the decorated function if authentication succeeds."""
        authentication_status = check_authentication(request.headers, request.json)
        if authentication_status == AuthenticationStatus.OK:
            return f(*args, **kwargs)
        else:
            return {'error': authentication_status}

    return decorated_function


def use_explorer(f):
    """
    Decorator that sets the specified explorer (if one is given) as a global variable before a request is executed
    and sets the global variable back to None at the end

    :param f: The function that requires an explorer
    :return: The result of the function
    """

    def decorated_function(*args, **kwargs):
        """Set explorer, execute function, and append explorer info to the result."""
        if request.query.explorer != '':
            set_explorer(request.query.explorer)

        ret = f(*args, **kwargs)
        if isinstance(ret, dict):
            ret['explorer'] = get_last_explorer()

        clear_explorer()
        return ret

    return decorated_function


def output_json(f):
    """
    Decorator that converts the return value of a function to a JSON string

    :param f: The function where the output needs to be converted to JSON string
    :return: The result of the function as a JSON string
    """

    def decorated_function(*args, **kwargs):
        """Execute function and return its output as a JSON string."""
        output = f(*args, **kwargs)
        if output is not None:
            return simplejson.dumps(output, indent=4, sort_keys=True)

    return decorated_function


def verify_config(section, option):
    """
    Decorator that verifies that a specific section and option are present in the configfile

    :param f: The function that requires information from the configfile
    :param section: The section that needs to be present in the configfile
    :param option: The option that needs to be present in the section of the configfile
    :return: The result of the function
    """

    def decorated_function(f):
        """Wrap the function with config verification logic."""
        @wraps(f)
        def wrapper(*args, **kwargs):
            """Execute the function after verifying config section and option exist."""
            # Read the spellbook configuration file
            config = ConfigParser()
            config.read(CONFIGURATION_FILE)

            # Check if the spellbook configuration file contains the section
            if not config.has_section(section):
                raise Exception('Configuration file %s does not have a [%s] section ' % (CONFIGURATION_FILE, section))

            # Check if the section has the option in it
            if not config.has_option(section, option):
                raise Exception("Configuration file %s does not have an option '%s' in the [%s] section" % (CONFIGURATION_FILE, option, section))

            return f(*args, **kwargs)

        return wrapper

    return decorated_function


def log_runtime(f):
    """
    Decorator that logs the runtime of a script
    """

    def decorated_function(*args, **kwargs):
        """Execute function and log its runtime."""
        start_time = time.time()
        output = f(*args, **kwargs)
        end_time = time.time()

        LOG.info('Script runtime: %s seconds' % (end_time - start_time))

        return output

    return decorated_function


def retry(retries=3):
    """Decorator that retries a function up to `retries` times on exception."""
    def decorator_retry(func):
        """Inner decorator that wraps the function with retry logic."""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            """Execute the function, retrying on failure with a 1-second delay."""
            for attempt in range(retries):
                try:
                    result = func(*args, **kwargs)
                    return result
                except Exception as e:
                    LOG.error(f"Error: {e}. Retrying... ({attempt + 1}/{retries})")
                    time.sleep(1)  # Wait for 1 second before retrying
            return None  # If all retries fail, return None or handle accordingly

        return wrapper

    return decorator_retry
