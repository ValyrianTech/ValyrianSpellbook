#!/usr/bin/env python
# -*- coding: utf-8 -*-
import platform


def format_args(args):
    """
    Format the args to pass to the subprocess
    Linux requires a string with spaces (if an argument contains spaces it must be surrounded with quotes), whereas Windows requires a list

    :param args: A list of arguments
    :return: The arguments as required by the operating system
    """
    if platform.system() == 'Linux':
        formatted_string = ''
        for arg in args:
            formatted_string += '%s ' % arg if ' ' not in arg else '"%s" ' % arg
        return formatted_string
    else:
        return args
