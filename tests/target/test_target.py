### SPDX-License-Identifier: GPL-2.0-or-later

"""Test cases for rsk_fsm.target builder implementations"""

import os

from unittest import TestCase

from rsk_mt.jsonschema.schema import (RootSchema, Support)

from rsk_fsm.build import (Fsm, State, Transition)
from rsk_fsm.target.c import Builder as CBuilder
from rsk_fsm.target.python import Builder as PythonBuilder

SCHEMA_FILE = '/usr/share/json-schema/rsk-fsm/fsm.json'

SCHEMA_URI = 'https://json-schema.roughsketch.co.uk/rsk-fsm/fsm.json'

BASES = {
    SCHEMA_URI + '#fsm': (Fsm,),
    SCHEMA_URI + '#state': (State,),
    SCHEMA_URI + '#transition': (Transition,),
}

PACKAGE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
TEST_FSM = os.path.join(PACKAGE_DIR, 'share/test.fsm')
TEST_OUT_C = os.path.join(PACKAGE_DIR, 'share/test_fsm.out')
TEST_OUT_PY = os.path.join(PACKAGE_DIR, 'share/test_fsm.py')

def _build(testcase):
    """Return target implementation of share/test.fsm for `testcase` builder"""
    # do not enforce formats, not under test
    schema = RootSchema.load(SCHEMA_FILE, support=Support(bases=BASES))
    with open(TEST_FSM, encoding='utf-8') as fid:
        fsm = schema.decode(fid.read())
    builder = testcase.get_builder(fsm['name'])
    implementation = builder.build(fsm)
    return str(implementation)

class TestTargetCBuilder(TestCase):
    """Test cases for rsk_fsm.target.c.Builder"""
    def __init__(self, *args):
        super().__init__(*args)
        self._reference = TEST_OUT_C
    @staticmethod
    def get_builder(prefix):
        """Return the builder to test"""
        return CBuilder(prefix)
    def get_output(self):
        """Return the reference output"""
        with open(self._reference, encoding='utf-8') as fid:
            return fid.read().rstrip()
    def test_build(self):
        """Test rsk_fsm.target.c.Builder builds share/test.fsm"""
        self.assertEqual(_build(self), self.get_output())

class TestTargetPythonBuilder(TestCase):
    """Test cases for rsk_fsm.target.python.Builder"""
    def __init__(self, *args):
        super().__init__(*args)
        self._reference = TEST_OUT_PY
    @staticmethod
    def get_builder(prefix):
        """Return the builder to test"""
        return PythonBuilder(prefix)
    def get_output(self):
        """Return the reference output"""
        with open(self._reference, encoding='utf-8') as fid:
            return fid.read().rstrip()
    def test_build(self):
        """Test rsk_fsm.target.python.Builder builds share/test.fsm"""
        self.assertEqual(_build(self), self.get_output())
