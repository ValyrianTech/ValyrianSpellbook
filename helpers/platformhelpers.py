#!/usr/bin/env python
"""Helper functions for platform-specific (OS) operations."""
import platform


def format_args(args):
    """
    Format the args to pass to the subprocess
    Linux requires a string with spaces (if an argument contains spaces it must be surrounded with quotes), whereas Windows requires a list

    :param args: A list of arguments
    :return: The arguments as required by the operating system
    """
    if platform.system() == 'Linux' and isinstance(args, list):
        formatted_string = ''
        for arg in args:
            formatted_string += f'{arg} ' if ' ' not in arg else f'"{arg}" '
        return formatted_string
    else:
        return args
