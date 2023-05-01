### SPDX-License-Identifier: GPL-2.0-or-later

"""Test cases for rsk_fsm.build"""

from unittest import TestCase

from rsk_fsm.build import (Fsm, State, Transition, Builder)

# pylint: disable=no-member

MockFsm = type('MockFsm', (dict, Fsm), {})
MockState = type('MockState', (dict, State), {})
MockTransition = type('MockTransition', (dict, Transition), {})

class TestFsmEmpty(TestCase):
    """Test cases for rsk_fsm.build.Fsm with empty spec"""
    def test_walk(self):
        """Test rsk_fsm.build.Fsm.walk with empty spec"""
        mock = MockFsm({})
        self.assertRaises(KeyError, mock.walk, self, None)
    def test_initial_state(self):
        """Test rsk_fsm.build.Fsm.initial_state with empty spec"""
        mock = MockFsm({})
        with self.assertRaises(KeyError):
            mock.initial_state # pylint: disable=pointless-statement

class TestFsmSimple(TestCase):
    """Test cases for rsk_fsm.build.Fsm with simple spec"""
    def __init__(self, *args):
        super().__init__(*args)
        self._first = MockState({'state': 'A'})
        self._second = MockState({'state': 'B'})
        self._mock = MockFsm({
            'initial': 'A',
            'states': [self._first, self._second],
        })
        self._walk = []
    def walk_push(self, state, data):
        """Record call for walk method test."""
        self._walk.append(('+', state, data))
    def walk_pop(self, state, data):
        """Record call for walk method test."""
        self._walk.append(('-', state, data))
    def test_walk(self):
        """Test rsk_fsm.build.Fsm.walk with simple spec"""
        walker = self
        self.assertEqual(self._mock, self._mock.walk(walker, 'foobar'))
        self.assertEqual(self._walk, [
            ('+', self._first, 'foobar'),
            ('-', self._first, 'foobar'),
            ('+', self._second, 'foobar'),
            ('-', self._second, 'foobar'),
        ])
    def test_initial_state(self):
        """Test rsk_fsm.build.Fsm.initial_state with simple spec"""
        self.assertEqual('A', self._mock.initial_state)

class TestStateEmpty(TestCase):
    """Test cases for rsk_fsm.build.State with empty spec"""
    def __init__(self, *args):
        super().__init__(*args)
        self._mock = MockState({})
        self._walk = []
    def walk_push(self, state, data):
        """Record call for walk method test."""
        self._walk.append(('+', state, data))
    def walk_pop(self, state, data):
        """Record call for walk method test."""
        self._walk.append(('-', state, data))
    def test_walk(self):
        """Test rsk_fsm.build.State.walk with empty spec"""
        walker = self
        self.assertEqual(self._mock, self._mock.walk(walker, None))
        self.assertEqual(self._walk, [
            ('+', self._mock, None),
            ('-', self._mock, None),
        ])
    def test_name(self):
        """Test rsk_fsm.build.State.name with empty spec"""
        with self.assertRaises(KeyError):
            self._mock.name # pylint: disable=pointless-statement
    def test_initial_state(self):
        """Test rsk_fsm.build.State.initial_state with empty spec"""
        self.assertIsNone(self._mock.initial_state)
    def test_exit_actions(self):
        """Test rsk_fsm.build.State.exit_actions with empty spec"""
        self.assertEqual([], self._mock.exit_actions)
    def test_enter_actions(self):
        """Test rsk_fsm.build.State.enter_actions with empty spec"""
        self.assertEqual([], self._mock.enter_actions)
    def test_transitions(self):
        """Test rsk_fsm.build.State.transitions with empty spec"""
        self.assertEqual([], list(self._mock.transitions))

class TestStateSimple(TestCase):
    """Test cases for rsk_fsm.build.State with simple spec"""
    def __init__(self, *args):
        super().__init__(*args)
        self._child = MockState({'state': 'child'})
        self._empty = MockTransition({})
        self._mock = MockState({
            'states': [self._child],
            'state': 'parent',
            'initial': 'child',
            'exit': ['foo'],
            'enter': ['bar', 'baz'],
            'transitions': [self._empty],
        })
        self._walk = []
    def walk_push(self, state, data):
        """Record call for walk method test."""
        self._walk.append(('+', state, data))
    def walk_pop(self, state, data):
        """Record call for walk method test."""
        self._walk.append(('-', state, data))
    def test_walk(self):
        """Test rsk_fsm.build.State.walk with simple spec"""
        walker = self
        self.assertEqual(self._mock, self._mock.walk(walker, 'quux'))
        self.assertEqual(self._walk, [
            ('+', self._mock, 'quux'),
            ('+', self._child, 'quux'),
            ('-', self._child, 'quux'),
            ('-', self._mock, 'quux'),
        ])
    def test_name(self):
        """Test rsk_fsm.build.State.name with simple spec"""
        self.assertEqual('parent', self._mock.name)
    def test_initial_state(self):
        """Test rsk_fsm.build.State.initial_state with simple spec"""
        self.assertEqual('child', self._mock.initial_state)
    def test_exit_actions(self):
        """Test rsk_fsm.build.State.exit_actions with simple spec"""
        self.assertEqual(['foo'], self._mock.exit_actions)
    def test_enter_actions(self):
        """Test rsk_fsm.build.State.enter_actions with simple spec"""
        self.assertEqual(['bar', 'baz'], self._mock.enter_actions)
    def test_transitions(self):
        """Test rsk_fsm.build.State.transitions with simple spec"""
        self.assertEqual([self._empty], list(self._mock.transitions))

class TestTransitionEmpty(TestCase):
    """Test cases for rsk_fsm.build.Transition with empty spec"""
    def test_event(self):
        """Test rsk_fsm.build.Transition.event with empty spec"""
        mock = MockTransition({})
        with self.assertRaises(KeyError):
            mock.event # pylint: disable=pointless-statement
    def test_condition(self):
        """Test rsk_fsm.build.Transition.condition with empty spec"""
        mock = MockTransition({})
        self.assertEqual((None, None), mock.condition)
    def test_actions(self):
        """Test rsk_fsm.build.Transition.actions with empty spec"""
        mock = MockTransition({})
        self.assertEqual([], mock.actions)
    def test_next_state(self):
        """Test rsk_fsm.build.Transition.next_state with empty spec"""
        mock = MockTransition({})
        self.assertEqual(False, mock.next_state)

class TestTransitionSimple(TestCase):
    """Test cases for rsk_fsm.build.Transition with simple spec"""
    def __init__(self, *args):
        super().__init__(*args)
        self._mock = MockTransition({
            'event': 'foo',
            'condition': 'bar',
            'actions': ['baz'],
            'next': 'quux',
        })
    def test_event(self):
        """Test rsk_fsm.build.Transition.event with simple spec"""
        self.assertEqual('foo', self._mock.event)
    def test_condition(self):
        """Test rsk_fsm.build.Transition.condition with simple spec"""
        self.assertEqual(('bar', True), self._mock.condition)
    def test_actions(self):
        """Test rsk_fsm.build.Transition.actions with simple spec"""
        self.assertEqual(['baz'], self._mock.actions)
    def test_next_state(self):
        """Test rsk_fsm.build.Transition.next_state with simple spec"""
        self.assertEqual('quux', self._mock.next_state)

class TestTransition(TestCase):
    """Test cases for rsk_fsm.build.Transition"""
    def test_transition_unconditional(self):
        """Test rsk_fsm.build.Transition.condition unconditional"""
        mock = MockTransition({})
        self.assertEqual((None, None), mock.condition)
    def test_transition_condition(self):
        """Test rsk_fsm.build.Transition.condition conditional"""
        mock = MockTransition({'condition': 'foo'})
        self.assertEqual(('foo', True), mock.condition)
    def test_transition_not_condition(self):
        """Test rsk_fsm.build.Transition.condition conditional not"""
        mock = MockTransition({'condition': {'not': 'foo'}})
        self.assertEqual(('foo', False), mock.condition)
    def test_transition_final_state(self):
        """Test rsk_fsm.build.Transition.next_state final state"""
        mock = MockTransition({'next': None})
        self.assertEqual(None, mock.next_state)

class TestBuilder(TestCase):
    """Test cases for rsk_fsm.build.Builder"""
    def __init__(self, *args):
        super().__init__(*args)
        self._builder = Builder('foo')
    def test_pointer_to_path_null(self):
        """Test rsk_fsm.build.Builder.pointer_to_path None"""
        with self.assertRaises(ValueError):
            self._builder.pointer_to_path(None)
    def test_pointer_to_path_false(self):
        """Test rsk_fsm.build.Builder.pointer_to_path False"""
        with self.assertRaises(ValueError):
            self._builder.pointer_to_path(False)
    def test_pointer_to_path_absolute(self):
        """Test rsk_fsm.build.Builder.pointer_to_path absolute-state-pointer"""
        self.assertEqual(
            ['A', 'B', 'C'],
            self._builder.pointer_to_path('/A/B/C'),
        )
    def test_pointer_to_path_relative(self):
        """Test rsk_fsm.build.Builder.pointer_to_path relative-state-pointer"""
        with self.assertRaises(ValueError):
            self._builder.pointer_to_path('.././A/B/C')
    def test_pointer_to_path_name(self):
        """Test rsk_fsm.build.Builder.pointer_to_path state-name"""
        with self.assertRaises(ValueError):
            self._builder.pointer_to_path('A')
    def test_path_to_pointer_empty(self):
        """Test rsk_fsm.build.Builder.path_to_pointer empty path"""
        with self.assertRaises(ValueError):
            self._builder.path_to_pointer([])
    def test_path_to_pointer_relative(self):
        """Test rsk_fsm.build.Builder.path_to_pointer relative state path"""
        with self.assertRaises(ValueError):
            self._builder.path_to_pointer(['..', 'A'])
    def test_path_to_pointer_absolute(self):
        """Test rsk_fsm.build.Builder.path_to_pointer absolute state path"""
        self.assertEqual(
            '/A',
            self._builder.path_to_pointer(['A']),
        )
        self.assertEqual(
            '/A/B/C',
            self._builder.path_to_pointer(['A', 'B', 'C']),
        )
    def test_no_implementation(self):
        """Test rsk_fsm.build.Builder.build is abstract"""
        mock = MockFsm({'initial': 'A', 'states': [MockState({'state': 'A'})]})
        with self.assertRaises(NotImplementedError):
            self._builder.build(mock)
    def test_builder_duplicate_states(self):
        """Test rsk_fsm.build.Builder.build rejects duplicate states"""
        fsm = MockFsm({
            'initial': 'A',
            'states': [MockState({'state': 'A'}), MockState({'state': 'A'})],
        })
        builder = Builder('dup')
        with self.assertRaises(ValueError):
            builder.build(fsm)
    def test_builder_bad_root_initial(self):
        """Test rsk_fsm.build.Builder.build rejects bad initial state"""
        fsm = MockFsm({
            'initial': 'A',
            'states': [MockState({'state': 'B'}), MockState({'state': 'C'})],
        })
        builder = Builder('ini')
        with self.assertRaises(ValueError):
            builder.build(fsm)
    def test_builder_bad_nested_initial(self):
        """Test rsk_fsm.build.Builder.build rejects bad nested initial state"""
        fsm = MockFsm({
            'initial': 'A',
            'states': [MockState({'state': 'A', 'initial': 'B'})],
        })
        builder = Builder('bnis')
        with self.assertRaises(ValueError):
            builder.build(fsm)
    def test_builder_bad_next_state(self):
        """Test rsk_fsm.build.Builder.build rejects bad next state"""
        fsm = MockFsm({
            'initial': 'A',
            'states': [
                MockState({
                    'state': 'A',
                    'transitions': [
                        MockTransition({'event': 'X', 'next': '/foo/bar'}),
                    ],
                }),
            ],
        })
        builder = Builder('bns')
        with self.assertRaises(ValueError):
            builder.build(fsm)

class _TargetBuilder(Builder):
    """A builder of target implementations comparable with test expectations"""
    def build_implementation(self):
        """Return a fixed dict of builder values"""
        return {
            'initial': self.initial,
            'states': sorted(self.states),
            'events': sorted(self.events),
            'conditions': sorted(self.conditions),
            'actions': sorted(self.actions),
            'initial_map': {_: self.initial_state(_) for _ in self.states},
            'transitions': dict([
                (None, {None: self.get_initial_transition()})
            ] + [
                (e, {s: self.get_transitions(e, s) for s in self.states})
                for e in self.events
            ]),
        }

class _BuilderTestBuilder(type):
    """Build tests for rsk_fsm.build.Builder test cases

    Specify this class as metaclass and provide:
    `name` - the test case name
    `spec` - the FSM specification
    `expect` - a dict of expected built values
    """
    def __new__(cls, name, bases, dct):
        built = _TargetBuilder('test').build(MockFsm(dct['spec']))
        for (key, val) in built.items():
            exp = dct['expect'][key]
            dct[f'test_{key}'] = cls.make_test(dct['name'], key, val, exp)
        return super().__new__(cls, name, bases, dct)
    @staticmethod
    def make_test(name, key, val, exp):
        """Make a function testing built `val` at `key` for test case `name`"""
        def method(self):
            """Test `val` equals `exp`"""
            self.assertEquals(val, exp)
        fqname = 'rsk_fsm.build.Builder.build'
        method.__doc__ = f'Test {fqname} builds expected {key} for FSM {name}'
        return method

class TestBuilderInitialTransition(TestCase, metaclass=_BuilderTestBuilder):
    """Test rsk_fsm.build.Builder building FSM initial transition"""
    name = 'initial transition'
    spec = {
        'initial': 'A',
        'states': [
            MockState({
                'state': 'A',
            }),
        ],
    }
    expect = {
        'initial': '/A',
        'states': ['/A'],
        'events': [],
        'conditions': [],
        'actions': [],
        'initial_map': {
            '/A': '/A',
        },
        'transitions': {
            None: {
                None: {
                    'steps': [
                        {'state': '/A'},
                        {'actions': []},
                    ],
                },
            },
        },
    }

class TestBuilderInitialStates(TestCase, metaclass=_BuilderTestBuilder):
    """Test rsk_fsm.build.Builder building FSM initial states"""
    name = 'initial states'
    spec = {
        'initial': 'A',
        'states': [
            MockState({
                'state': 'A',
                'enter': ['foo'],
                'initial': 'B',
                'states': [
                    MockState({
                        'state': 'B',
                        'initial': 'D',
                        'states': [
                            MockState({'state': 'C'}),
                            MockState({
                                'state': 'D',
                                'enter': ['bar'],
                            }),
                        ],
                    }),
                    MockState({
                        'state': 'E',
                        'enter': ['baz'],
                        'initial': 'F',
                        'states': [
                            MockState({'state': 'F'}),
                            MockState({'state': 'G'}),
                        ],
                    }),
                ],
            }),
        ],
    }
    expect = {
        'initial': '/A/B/D',
        'states': [
            '/A', '/A/B', '/A/B/C', '/A/B/D', '/A/E', '/A/E/F', '/A/E/G',
        ],
        'events': [],
        'conditions': [],
        'actions': ['bar', 'baz', 'foo'],
        'initial_map': {
            '/A': '/A/B/D',
            '/A/B': '/A/B/D',
            '/A/B/C': '/A/B/C',
            '/A/B/D': '/A/B/D',
            '/A/E': '/A/E/F',
            '/A/E/F': '/A/E/F',
            '/A/E/G': '/A/E/G',
        },
        'transitions': {
            None: {
                None: {
                    'steps': [
                        {'state': '/A'},
                        {'actions': ['foo']},
                        {'state': '/A/B'},
                        {'actions': []},
                        {'state': '/A/B/D'},
                        {'actions': ['bar']},
                    ],
                },
            },
        },
    }

class TestBuilderInternalTransition(TestCase, metaclass=_BuilderTestBuilder):
    """Test rsk_fsm.build.Builder building FSM internal transition"""
    name = 'internal transition'
    spec = {
        'initial': 'A',
        'states': [
            MockState({
                'state': 'A',
                'enter': ['foo'],
                'exit': ['bar'],
                'states': [
                    MockState({
                        'state': 'B',
                        'enter': ['baz'],
                        'exit': ['quux'],
                    }),
                ],
                'transitions': [
                    MockTransition({
                        'event': 'X',
                        'condition': 'corge',
                        'actions': ['grault'],
                    }),
                ],
            }),
        ],
    }
    expect = {
        'initial': '/A',
        'states': ['/A', '/A/B'],
        'events': ['X'],
        'conditions': ['corge'],
        'actions': ['bar', 'baz', 'foo', 'grault', 'quux'],
        'initial_map': {
            '/A': '/A',
            '/A/B': '/A/B',
        },
        'transitions': {
            None: {
                None: {
                    'steps': [
                        {'state': '/A'},
                        {'actions': ['foo']},
                    ],
                },
            },
            'X': {
                '/A': [{
                    'condition': 'corge', 'taken': True, 'steps': [
                        {'actions': ['grault']},
                    ],
                }],
                '/A/B': [{
                    'condition': 'corge', 'taken': True, 'steps': [
                        {'actions': ['grault']},
                    ],
                }],
            },
        },
    }

class TestBuilderExternalTransition(TestCase, metaclass=_BuilderTestBuilder):
    """Test rsk_fsm.build.Builder building FSM external transition"""
    name = 'external transition'
    spec = {
        'initial': 'A',
        'states': [
            MockState({
                'state': 'A',
                'initial': 'B',
                'enter': ['foo'],
                'exit': ['bar'],
                'states': [
                    MockState({
                        'state': 'B',
                        'enter': ['baz'],
                        'exit': ['quux'],
                    }),
                ],
                'transitions': [
                    MockTransition({
                        'event': 'X',
                        'condition': {'not': 'corge'},
                        'actions': ['grault'],
                        'next': 'C',
                    }),
                ],
            }),
            MockState({
                'state': 'C',
                'enter': ['thud'],
                'exit': ['wibble'],
                'transitions': [
                    MockTransition({
                        'event': 'X',
                        'actions': ['grault'],
                        'next': '.',
                    }),
                ],
            }),
        ],
    }
    expect = {
        'initial': '/A/B',
        'states': ['/A', '/A/B', '/C'],
        'events': ['X'],
        'conditions': ['corge'],
        'actions': ['bar', 'baz', 'foo', 'grault', 'quux', 'thud', 'wibble'],
        'initial_map': {
            '/A': '/A/B',
            '/A/B': '/A/B',
            '/C': '/C',
        },
        'transitions': {
            None: {
                None: {
                    'steps': [
                        {'state': '/A'},
                        {'actions': ['foo']},
                        {'state': '/A/B'},
                        {'actions': ['baz']},
                    ],
                },
            },
            'X': {
                '/A': [{
                    'condition': 'corge', 'taken': False, 'steps': [
                        {'actions': ['bar']},
                        {'state': '/A'},
                        {'actions': ['grault']},
                        {'state': '/C'},
                        {'actions': ['thud']},
                    ],
                }],
                '/A/B': [{
                    'condition': 'corge', 'taken': False, 'steps': [
                        {'actions': ['quux']},
                        {'state': '/A/B'},
                        {'actions': ['bar']},
                        {'state': '/A'},
                        {'actions': ['grault']},
                        {'state': '/C'},
                        {'actions': ['thud']},
                    ],
                }],
                '/C': [{
                    'condition': None, 'taken': None, 'steps': [
                        {'actions': ['wibble']},
                        {'state': '/C'},
                        {'actions': ['grault']},
                        {'state': '/C'},
                        {'actions': ['thud']},
                    ],
                }],
            },
        },
    }

class TestBuilderFinalTransition(TestCase, metaclass=_BuilderTestBuilder):
    """Test rsk_fsm.build.Builder building FSM final transition"""
    name = 'final transition'
    spec = {
        'initial': 'A',
        'states': [
            MockState({
                'state': 'A',
                'initial': 'B',
                'enter': ['foo'],
                'exit': ['bar'],
                'states': [
                    MockState({
                        'state': 'B',
                        'enter': ['baz'],
                        'exit': ['quux'],
                        'transitions': [
                            MockTransition({
                                'event': 'Y',
                                'actions': ['thud'],
                                'next': None,
                            }),
                        ],
                    }),
                ],
                'transitions': [
                    MockTransition({
                        'event': 'X',
                        'actions': ['wibble'],
                        'next': None,
                    }),
                ],
            }),
        ],
    }
    expect = {
        'initial': '/A/B',
        'states': ['/A', '/A/B'],
        'events': ['X', 'Y'],
        'conditions': [],
        'actions': ['bar', 'baz', 'foo', 'quux', 'thud', 'wibble'],
        'initial_map': {
            '/A': '/A/B',
            '/A/B': '/A/B',
        },
        'transitions': {
            None: {
                None: {
                    'steps': [
                        {'state': '/A'},
                        {'actions': ['foo']},
                        {'state': '/A/B'},
                        {'actions': ['baz']},
                    ],
                },
            },
            'X': {
                '/A': [{
                    'condition': None, 'taken': None, 'steps': [
                        {'actions': ['bar']},
                        {'state': '/A'},
                        {'state': None},
                        {'actions': ['wibble']},
                    ],
                }],
                '/A/B': [{
                    'condition': None, 'taken': None, 'steps': [
                        {'actions': ['quux']},
                        {'state': '/A/B'},
                        {'actions': ['bar']},
                        {'state': '/A'},
                        {'state': None},
                        {'actions': ['wibble']},
                    ],
                }],
            },
            'Y': {
                '/A': [],
                '/A/B': [{
                    'condition': None, 'taken': None, 'steps': [
                        {'actions': ['quux']},
                        {'state': '/A/B'},
                        {'actions': ['thud']},
                        {'state': '/A'},
                    ],
                }],
            },
        },
    }

class TestBuilderSiblingTransition(TestCase, metaclass=_BuilderTestBuilder):
    """Test rsk_fsm.build.Builder building FSM sibling transition"""
    name = 'sibling transition'
    spec = {
        'initial': 'A',
        'states': [
            MockState({
                'state': 'A',
                'enter': ['foo'],
                'exit': ['bar'],
                'initial': 'B',
                'states': [
                    MockState({
                        'state': 'B',
                        'enter': ['baz'],
                        'exit': ['quux'],
                        'transitions': [
                            MockTransition({
                                'event': 'X',
                                'condition': 'corge',
                                'actions': ['grault'],
                                'next': 'C',
                            }),
                            MockTransition({
                                'event': 'X',
                                'actions': ['frob'],
                                'next': '../D',
                            }),
                        ],
                    }),
                    MockState({
                        'state': 'C',
                        'enter': ['thud'],
                        'exit': ['quuz'],
                    }),
                    MockState({
                        'state': 'D',
                        'enter': ['thud'],
                        'exit': ['wibble'],
                        'initial': 'E',
                        'states': [
                            MockState({
                                'state': 'E',
                                'enter': ['flob'],
                                'exit': ['xyxxz'],
                            }),
                        ],
                        'transitions': [
                            MockTransition({
                                'event': 'Y',
                                'actions': ['grault'],
                                'next': '/A/B',
                            }),
                        ],
                    }),
                ],
            }),
        ],
    }
    expect = {
        'initial': '/A/B',
        'states': ['/A', '/A/B', '/A/C', '/A/D', '/A/D/E'],
        'events': ['X', 'Y'],
        'conditions': ['corge'],
        'actions': [
            'bar', 'baz',
            'flob', 'foo', 'frob',
            'grault',
            'quux', 'quuz',
            'thud',
            'wibble',
            'xyxxz'
        ],
        'initial_map': {
            '/A': '/A/B',
            '/A/B': '/A/B',
            '/A/C': '/A/C',
            '/A/D': '/A/D/E',
            '/A/D/E': '/A/D/E',
        },
        'transitions': {
            None: {
                None: {
                    'steps': [
                        {'state': '/A'},
                        {'actions': ['foo']},
                        {'state': '/A/B'},
                        {'actions': ['baz']},
                    ],
                },
            },
            'X': {
                '/A': [],
                '/A/B': [{
                    'condition': 'corge', 'taken': True, 'steps': [
                        {'actions': ['quux']},
                        {'state': '/A/B'},
                        {'actions': ['grault']},
                        {'state': '/A/C'},
                        {'actions': ['thud']},
                    ],
                }, {
                    'condition': None, 'taken': None, 'steps': [
                        {'actions': ['quux']},
                        {'state': '/A/B'},
                        {'actions': ['frob']},
                        {'state': '/A/D'},
                        {'actions': ['thud']},
                        {'state': '/A/D/E'},
                        {'actions': ['flob']},
                    ],
                }],
                '/A/C': [],
                '/A/D': [],
                '/A/D/E': [],
            },
            'Y': {
                '/A': [],
                '/A/B': [],
                '/A/C': [],
                '/A/D': [{
                    'condition': None, 'taken': None, 'steps': [
                        {'actions': ['wibble']},
                        {'state': '/A/D'},
                        {'actions': ['grault']},
                        {'state': '/A/B'},
                        {'actions': ['baz']},
                    ],
                }],
                '/A/D/E': [{
                    'condition': None, 'taken': None, 'steps': [
                        {'actions': ['xyxxz']},
                        {'state': '/A/D/E'},
                        {'actions': ['wibble']},
                        {'state': '/A/D'},
                        {'actions': ['grault']},
                        {'state': '/A/B'},
                        {'actions': ['baz']},
                    ],
                }],
            },
        },
    }

class TestBuilderPointerTransition(TestCase, metaclass=_BuilderTestBuilder):
    """Test rsk_fsm.build.Builder building FSM pointer transition"""
    name = 'pointer transition'
    spec = {
        'initial': 'A',
        'states': [
            MockState({
                'state': 'A',
                'enter': ['foo'],
                'transitions': [
                    MockTransition({
                        'event': 'Z',
                        'next': '.././.././B/C',
                    }),
                ],
            }),
            MockState({
                'state': 'B',
                'enter': ['baz'],
                'exit': ['quux'],
                'initial': 'C',
                'states': [
                    MockState({
                        'state': 'C',
                        'enter': ['thud'],
                        'exit': ['wibble'],
                        'transitions': [
                            MockTransition({
                                'event': 'X',
                                'actions': ['frob'],
                                'next': '/D/E',
                            }),
                        ],
                    }),
                ],
                'transitions': [
                    MockTransition({
                        'event': 'Y',
                        'next': './C',
                    }),
                ],
            }),
            MockState({
                'state': 'D',
                'enter': ['thud'],
                'exit': ['quuz'],
                'states': [
                    MockState({
                        'state': 'E',
                        'enter': ['flob'],
                        'exit': ['xyxxz'],
                        'transitions': [
                            MockTransition({
                                'event': 'Y',
                                'condition': {'not': 'corge'},
                                'actions': ['grault'],
                                'next': '/A',
                            }),
                        ],
                    }),
                ],
                'transitions': [
                    MockTransition({
                        'event': 'X',
                        'actions': ['wibble'],
                        'next': '../B',
                    }),
                    MockTransition({
                        'event': 'Y',
                        'condition': 'corge',
                        'actions': ['grault'],
                        'next': None,
                    }),
                ],
            }),
        ],
    }
    expect = {
        'initial': '/A',
        'states': ['/A', '/B', '/B/C', '/D', '/D/E'],
        'events': ['X', 'Y', 'Z'],
        'conditions': ['corge'],
        'actions': [
            'baz',
            'flob', 'foo', 'frob',
            'grault',
            'quux', 'quuz',
            'thud',
            'wibble',
            'xyxxz'
        ],
        'initial_map': {
            '/A': '/A',
            '/B': '/B/C',
            '/B/C': '/B/C',
            '/D': '/D',
            '/D/E': '/D/E',
        },
        'transitions': {
            None: {
                None: {
                    'steps': [
                        {'state': '/A'},
                        {'actions': ['foo']},
                    ],
                },
            },
            'X': {
                '/A': [],
                '/B': [],
                '/B/C': [{
                    'condition': None, 'taken': None, 'steps': [
                        {'actions': ['wibble']},
                        {'state': '/B/C'},
                        {'actions': ['quux']},
                        {'state': '/B'},
                        {'actions': ['frob']},
                        {'state': '/D'},
                        {'actions': ['thud']},
                        {'state': '/D/E'},
                        {'actions': ['flob']},
                    ],
                }],
                '/D': [{
                    'condition': None, 'taken': None, 'steps': [
                        {'actions': ['quuz']},
                        {'state': '/D'},
                        {'actions': ['wibble']},
                        {'state': '/B'},
                        {'actions': ['baz']},
                        {'state': '/B/C'},
                        {'actions': ['thud']},
                    ],
                }],
                '/D/E': [{
                    'condition': None, 'taken': None, 'steps': [
                        {'actions': ['xyxxz']},
                        {'state': '/D/E'},
                        {'actions': ['quuz']},
                        {'state': '/D'},
                        {'actions': ['wibble']},
                        {'state': '/B'},
                        {'actions': ['baz']},
                        {'state': '/B/C'},
                        {'actions': ['thud']},
                    ],
                }],
            },
            'Y': {
                '/A': [],
                '/B': [{
                    'condition': None, 'taken': None, 'steps': [
                        {'actions': []},
                        {'state': '/B/C'},
                        {'actions': ['thud']},
                    ],
                }],
                '/B/C': [{
                    'condition': None, 'taken': None, 'steps': [
                        {'actions': ['wibble']},
                        {'state': '/B/C'},
                        {'actions': []},
                        {'state': '/B/C'},
                        {'actions': ['thud']},
                    ],
                }],
                '/D': [{
                    'condition': 'corge', 'taken': True, 'steps': [
                        {'actions': ['quuz']},
                        {'state': '/D'},
                        {'state': None},
                        {'actions': ['grault']},
                    ]
                }],
                '/D/E': [{
                    'condition': 'corge', 'taken': False, 'steps': [
                        {'actions': ['xyxxz']},
                        {'state': '/D/E'},
                        {'actions': ['quuz']},
                        {'state': '/D'},
                        {'actions': ['grault']},
                        {'state': '/A'},
                        {'actions': ['foo']},
                    ],
                }, {
                    'condition': 'corge', 'taken': True, 'steps': [
                        {'actions': ['xyxxz']},
                        {'state': '/D/E'},
                        {'actions': ['quuz']},
                        {'state': '/D'},
                        {'state': None},
                        {'actions': ['grault']},
                    ],
                }],
            },
            'Z': {
                '/A': [{
                    'condition': None, 'taken': None, 'steps': [
                        {'actions': []},
                        {'state': '/A'},
                        {'actions': []},
                        {'state': '/B'},
                        {'actions': ['baz']},
                        {'state': '/B/C'},
                        {'actions': ['thud']},
                    ],
                }],
                '/B': [],
                '/B/C': [],
                '/D': [],
                '/D/E': [],
            },
        },
    }
