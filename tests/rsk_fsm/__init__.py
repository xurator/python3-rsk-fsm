### SPDX-License-Identifier: GPL-2.0-or-later

"""Common test functions"""

def make_fqname(subject):
    """Return the fully-qualified name of test `subject`."""
    if subject.__class__.__name__ == 'method':
        return '.'.join((
            subject.__self__.__module__,
            subject.__self__.__name__,
            subject.__name__,
        ))
    return '.'.join((
        subject.__module__,
        subject.__name__,
    ))

def make_params_values(values):
    """Return an iterable of values for use with `nose2.params`."""
    # quirk: "To pass a tuple as a simple value, wrap it in another tuple."
    return ((v,) if isinstance(v, tuple) else v for v in values)

def make_params_pairs(arg_values):
    """Return an iterable of pairs for use with `nose2.params`.

    Each element in `arg_values` is expected to be a 2-tuple (`arg`, `values`).
    Pairs are formed by pairing `arg` with each value in `values`.
    """
    return ((a, v) for (a, values) in arg_values for v in values)

def make_values_not_in(values, other):
    """Return a tuple of `values` not in `other`."""
    return tuple(v for v in values if v not in other)
