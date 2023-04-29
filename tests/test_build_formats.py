### SPDX-License-Identifier: GPL-2.0-or-later

"""Test cases for rsk_fsm.build.FORMATS"""

import re

from unittest import TestCase
from nose2.tools import params

from rsk_fsm.build import FORMATS

_REGEXP = dict((
    (fmt, re.compile(pattern)) for (fmt, pattern) in FORMATS
))

class TestAbsoluteStatePointer(TestCase):
    """Test cases for rsk_fsm.build.FORMATS absolute-state-pointer"""
    regexp = _REGEXP['absolute-state-pointer']
    @params(
        '/A',
        '/A/b',
        '/A/b/C_',
        '/A/b/C_/d-',
    )
    def test_match(self, string):
        """Test rsk_fsm.build.FORMATS absolute-state-pointer match"""
        self.assertIsNotNone(self.regexp.match(string))
    @params(
        '',
        'A',
        'A/b',
        '/A/b/C#',
        '/A/b//d-',
    )
    def test_no_match(self, string):
        """Test rsk_fsm.build.FORMATS absolute-state-pointer no match"""
        self.assertIsNone(self.regexp.match(string))

class TestRelativeStatePointer(TestCase):
    """Test cases for rsk_fsm.build.FORMATS relative-state-pointer"""
    regexp = _REGEXP['relative-state-pointer']
    @params(
        '.',
        '..',
        './.',
        './..',
        './A',
        '../..',
        '../.',
        '../A',
        '././A',
        './../A',
        '../../A',
        '.././A',
        './A/b',
        '../A/b',
        '././A/b',
        './../A/b',
        '../../A/b',
        '.././A/b',
        './A/b/C_',
        '././A/b/C_',
        './../A/b/C_',
        '../A/b/C_',
        '../../A/b/C_',
        '.././A/b/C_',
        './A/b/C_/d-',
        '././A/b/C_/d-',
        './../A/b/C_/d-',
        '../A/b/C_/d-',
        '../../A/b/C_/d-',
        '.././A/b/C_/d-',
    )
    def test_match(self, string):
        """Test rsk_fsm.build.FORMATS relative-state-pointer match"""
        self.assertIsNotNone(self.regexp.match(string))
    @params(
        '/A',
        '/A/b',
        '/A/b/C_',
        '/A/b/C_/d-',
        'A',
        'A/b',
        'A/b/C_',
        'A/b/C_/d-',
        '/',
        './',
        '.A',
        './/',
        '.A/',
        '../',
        '..A',
        '..//',
        '..A/',
        '../../',
        '../..A',
        '../..//',
        '../..A/',
        '...',
        '.../',
        'A/..',
        '../../A//C_/d-',
    )
    def test_no_match(self, string):
        """Test rsk_fsm.build.FORMATS relative-state-pointer no match"""
        self.assertIsNone(self.regexp.match(string))

class TestName(TestCase):
    """Test cases for rsk_fsm.build.FORMATS *-name"""
    regexp = _REGEXP['state-name']
    @params(
        'A',
        'Aa',
        'AA',
        'A_',
        'A-',
        'a',
        'aa',
        'aA',
        'A_',
        'A-',
    )
    def test_match(self, string):
        """Test rsk_fsm.build.FORMATS *-name match"""
        self.assertIsNotNone(self.regexp.match(string))
    @params(
        '',
        '_',
        '_a',
        '_A',
        '_-',
        '__',
        '-',
        '-b',
        '-B',
        '--',
        '-_',
        '#',
        'A#',
        'a#',
    )
    def test_no_match(self, string):
        """Test rsk_fsm.build.FORMATS *-name no match"""
        self.assertIsNone(self.regexp.match(string))
