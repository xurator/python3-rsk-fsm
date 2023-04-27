### SPDX-License-Identifier: GPL-2.0-or-later

"""Compile a FSM specification into a target implementation."""

from argparse import ArgumentParser
import re
import sys
from contextlib import nullcontext

from rsk_mt.jsonschema.schema import (RootSchema, Support)
from rsk_mt.jsonschema.formats import Format

from .build import (FORMATS, Fsm, State, Transition)

from .target.c import Builder as CBuilder
from .target.python import Builder as PythonBuilder

SCHEMA_URI = 'https://json-schema.roughsketch.co.uk/rsk-fsm/fsm.json'

BASES = {
    SCHEMA_URI + '#fsm': (Fsm,),
    SCHEMA_URI + '#state': (State,),
    SCHEMA_URI + '#transition': (Transition,),
}

BUILDERS = {
    'C': CBuilder,
    'Python': PythonBuilder,
}

class _FormatRegexp(Format):
    """A format enforcing a regular expression on string values."""
    def __init__(self, name, regexp):
        self.name = name
        self._regexp = re.compile(regexp)
    def __call__(self, val):
        return bool(self._regexp.search(val))
    def validates(self, primitive):
        return primitive == 'string'

def main():
    """Compile a FSM specification into a target implementation."""
    aparser = ArgumentParser(description=main.__doc__)
    aparser.add_argument(
        '-s', '--schema', default='/usr/share/json-schema/rsk-fsm/fsm.json',
        help="the JSON Schema to validate the input fsm against",
    )
    aparser.add_argument(
        '-p', '--prefix',
        help="implementation prefix (default: the FSM name is used)",
    )
    for (fmt, regexp) in FORMATS:
        aparser.add_argument(
            f'--{fmt}', default=regexp,
            help=f"regular expression for format {fmt} (default: {regexp!r})",
        )
    aparser.add_argument(
        'fsm',
        help="the JSON FSM file to compile, or '-' to read from stdin",
    )
    aparser.add_argument(
        'target', choices=tuple(BUILDERS),
        help="the target implementation",
    )
    args = aparser.parse_args()
    schema = RootSchema.load(args.schema, support=Support(
        bases=BASES,
        formats={
            fmt: _FormatRegexp(fmt, getattr(args, fmt.replace('-', '_')))
            for (fmt, _) in FORMATS
        },
    ))
    with (  open(args.fsm, encoding='utf-8')
            if args.fsm != '-' else
            nullcontext(sys.stdin)
        ) as fid:
        fsm = schema.decode(fid.read())
    try:
        prefix = args.prefix if args.prefix else fsm['name']
    except KeyError:
        sys.exit("FSM has no name: must supply a prefix")
    implementation = BUILDERS[args.target](prefix).build(fsm)
    print(str(implementation))

if __name__ == '__main__':
    main()
