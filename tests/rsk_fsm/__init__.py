### SPDX-License-Identifier: GPL-2.0-or-later

"""Common test functions"""

def make_fqname(cls):
    """Return the fully-qualified name of test subject `cls`"""
    return '.'.join((
        cls.__module__,
        cls.__name__,
    ))
