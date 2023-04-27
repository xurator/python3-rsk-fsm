### SPDX-License-Identifier: GPL-2.0-or-later

# pylint: disable=line-too-long

"""A library for FSM target implementation builders.

This library is written for FSMs which conform to `Hierarchical FSM Schema`_.

An application generating a target implementation using :class:`Builder` may
enforce string character sets according to its needs. The structure of the
following formatted strings must be enforced:

* absolute-state-pointer
* relative-state-pointer
* state-name
* event-name
* condition-name
* action-name

The library code in this module supports (at least) strings conforming to the
regular expression patterns in :data:`FORMATS`. This library always requires
that:

* "/" is used to separate state names in an absolute or relative state pointer;
* "." is used in a relative state pointer to specify the context state;
* ".." is used in a relative state pointer to specify the parent state of the
    context state.

.. _Hierarchical FSM Schema: https://json-schema.roughsketch.co.uk/rsk-fsmc/fsm.json
"""

# pylint: enable=line-too-long

NAME = r'[A-Za-z][A-Za-z_-]*'
ABSOLUTE_STATE_POINTER_RE = r'^(/' + NAME + r')+$'
RELATIVE_STATE_POINTER_RE = r'^(\.{1,2})(/\.{1,2})*' + r'(/' + NAME + r')*$'
NAME_RE = r'^' + NAME + r'$'

### a sequence of 2-tuples (format name, regular expression pattern)
FORMATS = (
    ('absolute-state-pointer', ABSOLUTE_STATE_POINTER_RE),
    ('relative-state-pointer', RELATIVE_STATE_POINTER_RE),
    ('state-name', NAME_RE),
    ('event-name', NAME_RE),
    ('condition-name', NAME_RE),
    ('action-name', NAME_RE),
)

class Fsm():
    """A mixin for a FSM conforming to `Hierarchical FSM Schema`_."""
    # pylint: disable=unsubscriptable-object
    def walk(self, walker, data):
        """Walk this FSM's states.

        For each root state in the FSM, call the state object's `walk` method
        with `walker` and `data`.
        """
        for state in self['states']:
            state.walk(walker, data)
        return self
    @property
    def initial_state(self):
        """Return the string name of the initial state of the FSM."""
        return self['initial']

class State():
    """A mixin for a state conforming to `Hierarchical FSM Schema`_."""
    # pylint: disable=unsubscriptable-object
    def walk(self, walker, data):
        """Walk this state and its child states.

        Call the `walk_push` method of `walker` with this state object and
        `data` before walking its child states. After walking child states call
        the `walk_pop` method of `walker` with this state object and `data`.
        """
        walker.walk_push(self, data)
        try:
            states = self['states']
        except KeyError:
            pass
        else:
            for state in states:
                state.walk(walker, data)
        walker.walk_pop(self, data)
        return self
    @property
    def name(self):
        """Return the string name of this state."""
        return self['state']
    @property
    def initial_state(self):
        """Return the string name of the initial state of this state.

        The initial state is a child state of this state.
        If there is no initial state for this state, return None.
        """
        try:
            return self['initial']
        except KeyError:
            return None
    @property
    def exit_actions(self):
        """Return the list of actions to perform on exit from this state.

        Return a list of string names in the order they were specified.
        """
        try:
            return self['exit']
        except KeyError:
            return []
    @property
    def enter_actions(self):
        """Return the list of actions to perform on entry to this state.

        Return a list of string names in the order they were specified.
        """
        try:
            return self['enter']
        except KeyError:
            return []
    @property
    def transitions(self):
        """Yield the transitions defined for this state.

        Yield transitions in the order they were specified.
        """
        try:
            for transition in self['transitions']:
                yield transition
        except KeyError:
            pass

class Transition():
    """A mixin for a transition conforming to `Hierarchical FSM Schema`_."""
    # pylint: disable=unsubscriptable-object
    @property
    def event(self):
        """Return the string name of the event triggering this transition."""
        return self['event']
    @property
    def condition(self):
        """Return a 2-tuple (name, taken) of the condition for this transition.

        The transition is triggered if the result of testing condition with
        string `name` meets the requirements of value `taken`.

        If `name` is None, then the transition is triggered unconditionally.

        If `taken` is None, then the transition is triggered unconditionally
        (and condition `name` need not be tested).

        If `taken` is False, then the transition is triggered if the result of
        testing condition `name` is a falsy value.

        If `taken` is True, then the transition is triggered if the result of
        testing condition `name` is a truthy value.
        """
        try:
            condition = self['condition']
        except KeyError:
            return (None, None)
        try:
            return (condition['not'], False)
        except TypeError:
            return (condition, True)
    @property
    def actions(self):
        """Return a list of actions to perform on transition.

        Return a list of string names in the order they were specified.
        """
        try:
            return list(self['actions'])
        except KeyError:
            return []
    @property
    def next_state(self):
        """Return the next state to transition to.

        The return value is either a string, False or None. When the return
        value is a string it may be an absolute state pointer, a relative state
        pointer, or a state name.

        If the return value is an absolute state pointer, the next state is the
        state addressed by the pointer, relative to the root of the FSM.

        If the return value is a relative state pointer, the next state is the
        state addressed by the pointer, relative to the state where the
        transition was specified.

        If the return value is a state name, the next state is the named sibling
        state, relative to the state where the transition was specified.

        If the return value is False, then the next state is the current state
        and the transition must be handled without leaving the current state.

        If the return value is None, then the next state is the final state,
        relative to the state where the transition was specified.
        """
        try:
            return self['next']
        except KeyError:
            return False

class Builder():
    """An abstract base class for building a target implementation of a FSM.

    A concrete (derived) class must implement :meth:`build_implementation`.

    A target implementation is built by calling this class's :meth:`build`.
    The following attributes and functions become available to the derived class
    :meth:`build_implementation` in order to serialise the FSM implementation:

    * :attr:`states`, a mapping of absolute state pointer to State object
    * :attr:`events`, the set of FSM event names
    * :attr:`conditions`, the set of FSM condition names
    * :attr:`actions`, the set of FSM (entry, exit, transition) action names
    * :meth:`get_initial_transition`, returns the initial transition definition
    * :meth:`get_transitions`, returns a list of state transition definitions

    Each transition definition is a dict specifying the transition to implement.
    The definition 'steps' is a list of dicts, with each dict defining either
    'actions', a list of action names to perform in order, or 'state', the new
    state of the FSM as an absolute state pointer. The definition may optionally
    include 'condition' and 'taken'. If 'condition' and 'taken' are absent, or
    either has the value None, then the transition is unconditional. Otherwise
    the transition is conditional: it is only taken if the named 'condition'
    returns a result consistent with 'taken'.

    If `taken` is True, then the transition is taken if the named condition
    returns a truthy value; otherwise `taken` is False and the transition is
    taken if the named condition returns a falsy value.
    """
    def __init__(self, prefix):
        self._prefix = prefix
        self.initial = None
        self.states = {}
        self.events = set()
        self.conditions = set()
        self.actions = set()
    @staticmethod
    def error_not_a_state(string):
        """Raise :class:`ValueError`: the state in `string` is not a state."""
        raise ValueError(string + ' is not a defined state')
    @staticmethod
    def pointer_to_path(pointer):
        """Return a path, a list of state names, from absolute state `pointer`.

        Raise :class:`ValueError` if `pointer` is not an absolute state pointer.
        """
        try:
            path = pointer.split('/')
        except AttributeError:
            pass
        else:
            if path[0] == '':
                return path[1:]
        raise ValueError(pointer)
    @staticmethod
    def path_to_pointer(path):
        """Return an absolute state pointer corresponding to `path`.

        `path` must be a list of state names. Raise :class:`ValueError` if an
        absolute state pointer cannot be formed from `path`.
        """
        if not path or path[0].startswith('.'):
            raise ValueError(path)
        return '/' + '/'.join(path)
    def build(self, fsm):
        """Build and return the target implementation of `fsm`.

        This method requires that:
        - `fsm` is an object that implements :class:`Fsm`
        - all states in `fsm` implement :class:`State`
        - all state transitions implement :class:`Transition`
        """
        # prime instance variables for building
        fsm.walk(self, [])
        # integrity check the FSM
        self._check_states(fsm.initial_state)
        self._check_transitions()
        # set the initial state pointer
        self.initial = self.initial_state(
            self.path_to_pointer([fsm.initial_state]),
        )
        # build the target implementation
        implementation = self.build_implementation()
        # clear instance variables for the next call to build
        self.initial = None
        self.states = {}
        self.events = set()
        self.conditions = set()
        self.actions = set()
        return implementation
    def _check_states(self, initial):
        """Perform an integrity check of the FSM states.

        `initial` is the state name of the declared initial state of the FSM.

        Raise :class:`ValueError` if there is a specification error in the FSM
        state hierarchy.
        """
        if self.path_to_pointer([initial]) not in self.states:
            self.error_not_a_state(f'initial state "{initial}" of FSM')
        for (pointer, state) in self.states.items():
            i_name = state.initial_state
            if i_name is None:
                continue
            i_pointer = self.path_to_pointer(
                self.pointer_to_path(pointer) + [i_name]
            )
            if i_pointer not in self.states:
                self.error_not_a_state(
                    f'initial state "{i_name}" of state "{pointer}"'
                )
    def _check_transitions(self):
        """Perform an integrity check of the FSM transitions.

        Raise :class:`ValueError` if there is a specification error in a FSM
        transition.
        """
        for (pointer, state) in self.states.items():
            path = self.pointer_to_path(pointer)
            for transition in state.transitions:
                if transition.next_state is False:
                    continue
                try:
                    self._next_state(transition.next_state, list(path))
                except ValueError:
                    self.error_not_a_state(
                        f'next state "{transition.next_state}"'
                        f' of transition from state "{pointer}"'
                    )
    def walk_push(self, state, path):
        """Walk callback: walking `state` under `path`."""
        # record `state` against its absolute state pointer
        path.append(state.name)
        pointer = self.path_to_pointer(path)
        if pointer in self.states:
            raise ValueError(f'duplicate state {pointer}')
        self.states[pointer] = state
        # accumulate action, event and condition names
        for action in state.exit_actions:
            self.actions.add(action)
        for action in state.enter_actions:
            self.actions.add(action)
        for transition in state.transitions:
            self.events.add(transition.event)
            condition = transition.condition[0]
            if condition:
                self.conditions.add(condition)
            for action in transition.actions:
                self.actions.add(action)
        return self
    def walk_pop(self, state, path): # pylint: disable=unused-argument
        """Walk callback: walked `state` under `path`."""
        path.pop()
        return self
    def build_implementation(self):
        """Build and return the target implementation."""
        raise NotImplementedError
    def initial_state(self, pointer):
        """Return a pointer to the initial state of the state at `pointer`.

        Return an absolute pointer to the nested initial state of the state
        pointed to by absolute `pointer`. If the state does not have any
        substates or does not specify an initial state, then the initial state
        is the state itself and `pointer` is returned.

        Raise :class:`ValueError` if `pointer` does not point to a state.
        """
        try:
            state = self.states[pointer]
        except KeyError:
            raise ValueError(pointer) # pylint: disable=raise-missing-from
        path = self.pointer_to_path(pointer)
        while state.initial_state:
            path.append(state.initial_state)
            pointer = self.path_to_pointer(path)
            state = self.states[pointer]
        return pointer
    def _exit_steps(self, src, dst):
        """Return a list of the exit steps to take for an external transition.

        The external transition is from the state pointed to by absolute pointer
        `src`. If `dst` is an absolute pointer then it points to the next state
        after the transition. Otherwise `dst` must be None, which indicates that
        this is a final transition of the FSM.
        """
        if src == dst:
            # exit `src` for an external transition to the same state
            return [
                {'actions': self.states[src].exit_actions},
                {'state': src},
            ]
        # exit each state from `src` up to the common parent of `src` and `dst`
        src_path = self.pointer_to_path(src)
        dst_path = self.pointer_to_path(dst) if dst else []
        steps = []
        path = list(src_path)
        while path != dst_path[:len(path)]:
            pointer = self.path_to_pointer(path)
            path.pop()
            # perform exit actions before formally leaving the state
            steps += [
                {'actions': self.states[pointer].exit_actions},
                {'state': pointer},
            ]
        return steps
    def _enter_steps(self, src, dst):
        """Return a list of the enter steps to take for an external transition.

        The external transition is to the state pointed to by absolute pointer
        `dst`. If `src` is an absolute pointer then it points to the state
        before the transition. Otherwise `src` must be None, which indicates
        that this is the initial transition of the FSM.
        """
        if src == dst:
            # enter `dst` for an external transition to the same state
            return [
                {'state': dst},
                {'actions': self.states[dst].enter_actions},
            ]
        # enter each state from the common parent with `src` down to `dst`
        src_path = self.pointer_to_path(src) if src else []
        dst_path = self.pointer_to_path(dst)
        steps = []
        path = list(src_path)
        # pop up to the common parent of `src` and `dst`
        while path != dst_path[:len(path)]:
            path.pop()
        if path == dst_path:
            # no enter actions to perform as target state is the common parent
            pointer = self.path_to_pointer(path)
            steps += [
                {'state': pointer},
            ]
        else:
            # enter each state from the common parent of `src` and `dst`,
            # down to `dst`
            while path != dst_path:
                path.append(dst_path[len(path)])
                pointer = self.path_to_pointer(path)
                # perform enter actions after formally entering the state
                steps += [
                    {'state': pointer},
                    {'actions': self.states[pointer].enter_actions},
                ]
        return steps
    def get_initial_transition(self):
        """Return a dict with 'steps' for the initial transition of the FSM."""
        return {'steps': self._enter_steps(None, self.initial)}
    def _next_state(self, next_state, path):
        """Return an absolute state pointer to `next_state` relative to `path`.

        Return the absolute state pointer corresponding to `next_state` relative
        to the context state at `path`, or None if the next state is the final
        state of the FSM. `next_state` must either be an absolute or relative
        state pointer, a state name or None (indicating a final state). Raise
        :class:`ValueError` if a valid return value cannot be formed (the next
        state is not defined in the FSM).
        """
        if next_state is None:
            # final state, relative to `path`
            path.pop()
            return self.path_to_pointer(path) if path else None
        if next_state.startswith('/'):
            # absolute state pointer
            dst = next_state
        elif next_state.startswith('.'):
            # relative state pointer, relative to `path`
            for elem in next_state.split('/'):
                if elem == '.':
                    continue
                if elem == '..':
                    try:
                        path.pop()
                    except IndexError:
                        pass
                else:
                    path.append(elem)
            dst = self.path_to_pointer(path)
        else:
            # (sibling) state name, relative to `path`
            path[-1] = next_state
            dst = self.path_to_pointer(path)
        return self.initial_state(dst)
    def get_transitions(self, event, src):
        """Return a list of dicts with 'steps' for handling `event`.

        Return a list of dicts defining how to handle `event` in the state
        addressed by absolute state pointer `src`. Each object in the list
        defines steps for either a conditional transition or an unconditional
        transition in the FSM. The generated list respects both the nesting
        order of states and the specified order of transitions. If an
        unconditional transition is encountered while generating the list, no
        further objects will be added to the list.
        """
        path = self.pointer_to_path(src)
        # inherit transitions in reverse state nesting order
        transitions = []
        while path:
            state = self.states[self.path_to_pointer(path)]
            for transition in state.transitions:
                if transition.event != event:
                    continue
                if transition.next_state is False:
                    # internal transition: never leave current state
                    steps = [
                        {'actions': transition.actions},
                    ]
                else:
                    # external transition: always leave current state
                    dst = self._next_state(transition.next_state, list(path))
                    steps = []
                    steps += self._exit_steps(src, dst)
                    if not dst:
                        steps += [
                            {'state': None},
                        ]
                    steps += [
                        {'actions': transition.actions},
                    ]
                    if dst:
                        steps += self._enter_steps(src, dst)
                (condition, taken) = transition.condition
                transitions.append({
                    'condition': condition,
                    'taken': taken,
                    'steps': steps,
                })
                if condition is None:
                    # unconditional transition: ignore further transitions
                    return transitions
            path.pop()
        return transitions
