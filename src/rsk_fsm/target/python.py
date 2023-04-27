### SPDX-License-Identifier: GPL-2.0-or-later

"""Build a Python implementation of a FSM."""

from ..build import Builder as _Builder

INDENT = ' ' * 4

def indent(stmt):
    """Return a string with each line in `stmt`, indented by :data:`INDENT`."""
    return INDENT + ('\n' + INDENT).join(str(stmt).split('\n'))

def docstring(string):
    """Return Python source for docstring `string`."""
    return '"""' + string + '"""'

def comment(string):
    """Return Python source for comment `string`."""
    return '# ' + string

def assignment(var, val):
    """Return Python source for assignment of `val` to `var`."""
    return f'{var} = {val}'

def call(expr, args):
    """Return Python source for calling function `expr` with `args`."""
    return f'{expr}({", ".join(args)})'

def try_block(stmt, exception):
    """Return Python source for try `stmt`, ignoring `exception`."""
    return '\n'.join([
        'try:',
        indent(stmt),
        f'except {exception}:',
        indent('pass'),
    ])

def if_then(expr, taken, block):
    """Return Python source for conditionally executing `block` statements.

    `block` statements are executed if `expr` returns `taken` boolean.
    """
    taken = '' if taken else 'not '
    return f'if {taken}{expr}:' + '\n' + '\n'.join([indent(_) for _ in block])

class Block():
    """Python statements block."""
    def __init__(self, stmts=()):
        self._stmts = list(stmts)
    def statement(self, stmt):
        """Append statement `stmt` to this block."""
        self._stmts.append(stmt)
    def statements(self, *stmts):
        """Append each statement in `stmts` to this block."""
        self._stmts.extend(stmts)
    def __iter__(self):
        return iter(self._stmts)
    def __str__(self):
        return '\n'.join([str(_) for _ in self._stmts])

class Function():
    """Python function."""
    def __init__(self, name, decorator=None, args=(), doc=None):
        self._name = name
        self._decorator = decorator
        self._args = args
        self._doc = docstring(doc) if doc else None
        self._stmts = []
    def statement(self, stmt):
        """Append statement `stmt` to this function."""
        self._stmts.append(stmt)
    def statements(self, *stmts):
        """Append each statement in `stmts` to this function."""
        self._stmts.extend(stmts)
    def __str__(self):
        stmts = []
        if self._decorator:
            stmts.append(self._decorator)
        stmts.append(f'def {self._name}({", ".join(self._args)}):')
        subs = [self._doc] if self._doc else []
        subs += self._stmts if self._stmts else ['pass']
        return '\n'.join(stmts) + '\n' + '\n'.join([indent(_) for _ in subs])
    @classmethod
    def static(cls, name, args=(), doc=None):
        """Return Python source for a staticmethod."""
        return cls(name, '@staticmethod', args, doc)
    @classmethod
    def method(cls, name, args=(), doc=None):
        """Return a new object for a Python method."""
        return cls(name, args=('self',) + tuple(args), doc=doc)

class Class(): # pylint: disable=too-few-public-methods
    """Python class."""
    def __init__(self, name, bases=('object',), doc=None):
        self._name = name
        self._bases = bases
        self._doc = docstring(doc) if doc else None
        self._stmts = []
    def statement(self, stmt):
        """Append statement `stmt` to this class."""
        self._stmts.append(stmt)
    def __str__(self):
        stmt = f'class {self._name}({", ".join(self._bases)}):'
        subs = [self._doc] if self._doc else []
        subs += self._stmts if self._stmts else ['pass']
        return stmt + '\n' + '\n'.join([indent(_) for _ in subs]) + '\n'

class Implementation(): # pylint: disable=too-many-instance-attributes
    """An instance of this class is a FSM implemented in Python.

    The string representation is the Python source code implementation.
    """
    callback_args = ('fsm', 'arg')
    def __init__(self, prefix, label, states, events, conditions, actions): # pylint: disable=too-many-arguments
        self._prefix = prefix
        ### the function for generating a state label from a state pointer
        self._label = label
        self._states = states
        self._events = events
        self._conditions = conditions
        self._actions = actions
        self._initial_transition = None
        self._event_transitions = {}
    def initial_transition(self, transition):
        """Record `transition` as the initial transition."""
        self._initial_transition = transition
    def event_transitions(self, event, state, transitions):
        """Record `transitions` as the transitions on `event` in `state`."""
        try:
            self._event_transitions[event][state] = transitions
        except KeyError:
            self._event_transitions[event] = {state: transitions}
    def _state_label(self, state):
        """Return a Python variable name for use as a state label."""
        return 'STATE_' + self._label(state)
    def _steps_to_statements(self, steps):
        """A generator yielding statements implementing transition `steps`."""
        for step in steps:
            try:
                actions = step['actions']
            except KeyError:
                pass
            else:
                for action in actions:
                    yield call(
                        f'fsm.callbacks.action_{action}',
                        self.callback_args,
                    )
            try:
                next_ = step['state']
            except KeyError:
                pass
            else:
                yield assignment(
                    'fsm.state',
                    self._state_label(next_) if next_ else None,
                )
    def _transition_function(self, name, doc, transitions):
        """Return a :class:`Function` implementing steps for `transitions`."""
        func = Function(name, args=self.callback_args, doc=doc)
        for transition in transitions:
            block = Block(list(self._steps_to_statements(transition['steps'])))
            try:
                condition = transition['condition']
            except KeyError:
                condition = None
            if condition:
                block.statement('return')
                expr = f'fsm.callbacks.condition_{condition}(fsm, arg)'
                taken = transition['taken']
                func.statement(if_then(expr, taken, block))
            else:
                func.statement(block)
        return func
    @property
    def _globals_block(self):
        """Return a :class:`Block` of global source code statements."""
        block = Block([
            docstring(f'A Python implementation of {self._prefix} FSM'),
            '',
            comment('pylint: disable=invalid-name'),
            '',
        ])
        ### enum of state constants
        for (idx, state) in enumerate(self._states):
            block.statement(
                assignment(self._state_label(state), idx),
            )
        block.statement('')
        ### function for the initial transition
        block.statements(
            self._transition_function(
                'initial_transition',
                'Transition into the initial state',
                [self._initial_transition],
            ),
            '',
        )
        ### functions and handler mappings for event transitions
        for event in self._events:
            handlers = []
            for state in self._states:
                try:
                    transitions = self._event_transitions[event][state]
                except KeyError:
                    continue
                name = f'handle_{event}_in_{self._label(state)}'
                block.statement(
                    self._transition_function(
                        name,
                        f'Handle event {event} in state {state}',
                        transitions,
                    ),
                )
                block.statement('')
                handlers.append(f'{self._state_label(state)}: {name},')
            if handlers:
                block.statement(
                    assignment(
                        f'TRANSITION_ON_EVENT_{event}',
                        '\n'.join([
                            '{'
                        ] + [
                            indent(h) for h in handlers
                        ] + [
                            '}',
                        ]),
                    ),
                )
                block.statement('')
        return block
    @property
    def _callbacks_class(self):
        """Return a :class:`Class` for callbacks."""
        doc = f'Interface for {self._prefix} FSM condition and action callbacks'
        cls = Class('Callbacks', doc=doc)
        not_implemented = 'raise NotImplementedError'
        for condition in self._conditions:
            name = f'condition_{condition}'
            doc = f'Callback for {self._prefix} FSM condition {condition}'
            method = Function.static(name, args=self.callback_args, doc=doc)
            method.statement(not_implemented)
            cls.statement(method)
        for action in self._actions:
            name = f'action_{action}'
            doc = f'Callback for {self._prefix} FSM action {action}'
            method = Function.static(name, args=self.callback_args, doc=doc)
            method.statement(not_implemented)
            cls.statement(method)
        return cls
    @property
    def _fsm_class(self):
        """Return a :class:`Class` for FSM."""
        cls = Class('Fsm', doc=f'A class for {self._prefix} FSM instances')
        method = Function.method(
            '__init__',
            args=('callbacks=None', 'data=None', 'arg=None'),
        )
        method.statements(
            assignment(
                'self.state',
                'None',
            ),
            assignment(
                'self.callbacks',
                'self if callbacks is None else callbacks',
            ),
            assignment(
                'self.data',
                'self if data is None else data',
            ),
            call(
                'initial_transition',
                ('self', 'arg'),
            ),
        )
        cls.statement(method)
        for event in self._events:
            args = list(self.callback_args)
            method = Function.method(
                f'inject_{event}',
                args=(f'{a}=None' for a in args[1:]),
                doc=f'Inject event {event} with event `arg`',
            )
            args[0] = 'self' # provide FSM instance as `fsm`
            method.statement(
                try_block(
                    call(
                        f'TRANSITION_ON_EVENT_{event}[self.state]',
                        args,
                    ),
                    'KeyError',
                ),
            )
            cls.statement(method)
        return cls
    def __str__(self):
        return '\n'.join((
            str(b) for b in (
                self._globals_block,
                self._callbacks_class,
                self._fsm_class,
            )
        ))

class Builder(_Builder):
    """A builder for target implementation of a FSM in Python."""
    def pointer_to_state_label(self, pointer):
        """Return a label for a state from absolute state `pointer`."""
        return '_'.join(self.pointer_to_path(pointer))
    def build_implementation(self):
        states = sorted(self.states)
        events = sorted(self.events)
        conditions = sorted(self.conditions)
        actions = sorted(self.actions)
        impl = Implementation(
            self._prefix,
            self.pointer_to_state_label,
            states,
            events,
            conditions,
            actions,
        )
        transition = self.get_initial_transition()
        impl.initial_transition(transition)
        for event in events:
            for state in self.states:
                transitions = self.get_transitions(event, state)
                if not transitions:
                    continue
                impl.event_transitions(event, state, transitions)
        return impl
