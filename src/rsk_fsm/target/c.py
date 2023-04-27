### SPDX-License-Identifier: GPL-2.0-or-later

"""Build a C implementation of a FSM."""

from ..build import Builder as _Builder

class Comment(): # pylint: disable=too-few-public-methods
    """C comment.

    Reference: K&R ANSI C Section A2.2
    """
    def __init__(self, txt):
        self.comments = txt.rstrip().split('\n')
    def __str__(self):
        if len(self.comments) == 1:
            return f'/* {self.comments[0]} */'
        return '\n'.join([
            '/* ' + self.comments[0]
        ] + [
            ' * ' + c for c in self.comments[1:]
        ] + [
            ' */'
        ])

class IfCondition(): # pylint: disable=too-few-public-methods
    """C if statement.

    Reference: K&R ANSI C Section A9.4
    """
    def __init__(self, expr, stmts, taken=True):
        self.expr = expr
        self.stmts = stmts
        self.taken = taken
    def __str__(self):
        condition = self.expr if self.taken else f'!({self.expr})'
        return '\n'.join([
            'if (' + condition + ') {'
        ] + [
            '\t' + str(s) for s in self.stmts
        ] + [
            '}',
        ])

class Declarator():
    """C declarator.

    - `identifier` is a string
    - `type_` is an instance of :class:`Type`
    - `type_name` is an explicit string type name

    Reference: K&R ANSI C Section A8.5
    """
    def __init__(self, identifier=None, type_=None, type_name=None):
        self._identifier = identifier
        self._type = type_
        if type_name:
            self._type_name = type_name
        elif type_:
            self._type_name = type_.typedef_name
        else:
            self._type_name = 'void'
    def __str__(self):
        if self._identifier:
            return f'{self._type_name} {self._identifier}'
        return self._type_name
    def __eq__(self, val):
        if self.identifier != val.identifier:
            return False
        if self.type_ != val.type_:
            return False
        if self.__class__ != val.__class__:
            return False
        return True
    @property
    def identifier(self):
        """Return this instance's identifier string."""
        return self._identifier
    @property
    def type_(self):
        """Return this instance's type object."""
        return self._type

class IndirectDeclarator(Declarator):
    """C indirect declarator.

    Reference: K&R ANSI C Section A8.5
    """
    def __init__(self, identifier, type_=None, type_name=None):
        super().__init__(identifier, type_, type_name)
    def __str__(self):
        if self._type:
            return f'{self._type.type_pointer} {self._identifier}'
        return f'{self._type_name} * {self._identifier}'

class Type():
    """A base class for C Types.

    Reference: K&R ANSI C Section A8.8, A8.9
    """
    def __init__(self, prefix):
        self._prefix = prefix
    def __str__(self):
        return self.typedef_name
    @property
    def type_specifier(self):
        """Return this instance's type-specifier string."""
        raise NotImplementedError
    @property
    def typedef_name(self):
        """Return this instance's typedef name string."""
        raise NotImplementedError
    @property
    def typedef(self):
        """Return this instance's typedef declaration string."""
        return f'typedef {self.type_specifier} {self.typedef_name};'
    @property
    def type_pointer(self):
        """Return this instance's type pointer string."""
        return f'{self.typedef_name} *'
    @property
    def opaque_type(self):
        """Return this instance's opaque type string."""
        raise NotImplementedError
    @property
    def null_value(self):
        """Return this instance's null value."""
        return 0
    def pointer(self, identifier):
        """Return an :class:`IndirectDeclarator` instance.

        Return an instance formed from `identifier` and this type.
        """
        return IndirectDeclarator(identifier, self)
    def variable(self, identifier, opaque=False):
        """Return a :class:`Declarator` instance.

        Return an instance formed from `identifier` and this type. If `opaque`
        then this type's :attr:`opaque_type` is used as an explicit type name.
        """
        if opaque:
            return Declarator(identifier, self, self.opaque_type)
        return Declarator(identifier, self)

class FunctionType(Type):
    """C function types.

    - `prefix` is a string prefix for the function typedef-name
    - `return_type` is a string, the function return type name
    - `parameters` is an iterable of :class:`Declarator` instances, the function
      formal parameters

    Reference: K&R ANSI C Section A8.6.3
    """
    def __init__(self, prefix, return_type=None, parameters=()):
        super().__init__(prefix)
        self._return_type = return_type if return_type else 'void'
        self._parameters = list(parameters)
    @property
    def typedef_name(self):
        return f'{self._prefix}_fp'
    @property
    def typedef(self):
        return (
            f'typedef {self._return_type} (*{self.typedef_name})'
            f'({", ".join([str(p) for p in self.parameters])});'
        )
    @property
    def type_pointer(self):
        return self.typedef_name
    @property
    def opaque_type(self):
        raise NotImplementedError
    def append(self, declarator):
        """Append `declarator` to this instance's formal parameters."""
        self._parameters.append(declarator)
    def extend(self, declarators):
        """Extend `declarators` to this instance's formal parameters."""
        self._parameters.extend(declarators)
    @property
    def parameters(self):
        """Yield each declarator in this instance's formal parameters.

        If this instance has no formal parameters, yield an empty declarator.
        """
        if not self._parameters:
            yield Declarator()
        else:
            for declarator in self._parameters:
                yield declarator
    def parameter(self, declarator):
        """Return the first parameter whose value is equal to `declarator`.

        Otherwise return None.
        """
        for parameter in self._parameters:
            if parameter == declarator:
                return parameter
        return None
    def interface(self, identifier):
        """Return the interface string for a function with name `identifier`."""
        return (
            f'{self._return_type} {identifier}'
            f'({", ".join([str(_) for _ in self.parameters])})'
        )

class Enum(Type):
    """C enumerations.

    - `prefix` is a string prefix for the type-specifier and typedef-name

    Reference: K&R ANSI C Section A8.4
    """
    def __init__(self, prefix):
        super().__init__(prefix)
        self._labels = []
    @property
    def type_specifier(self):
        return f'enum {self._prefix}_tag'
    @property
    def typedef_name(self):
        return f'{self._prefix}_e'
    @property
    def opaque_type(self):
        return 'int'
    @property
    def null_value(self):
        """Return the formatted label string for the null value."""
        return f'INVALID_{self._prefix.upper()}'
    def label_value(self, label):
        """Return the formatted label string for `label`.

        Raise :class:`ValueError` if `label` is not a declared label.
        """
        if label not in self._labels:
            raise ValueError(label)
        return f'{self._prefix.upper()}_{str(label).upper()}'
    @property
    def label_values(self):
        """Yield this instance's formatted label strings.

        Yield formatted label strings in the order of declaration.
        """
        for label in self._labels:
            yield self.label_value(label)
    @property
    def num_values(self):
        """Return the formatted label string for the number of labels."""
        return f'NUM_{self._prefix.upper()}'
    def append(self, label):
        """Append `label` string to this instance's declared labels."""
        self._labels.append(label)
    def extend(self, labels):
        """Extend `labels` strings to this instance's declared labels."""
        self._labels.extend(labels)
    def index(self, label):
        """Return the index of `label` in this instance's declared labels."""
        return self._labels.index(label)
    @property
    def labels(self):
        """Yield all formatted label values for this instance.

        Yield the null value, label values, finally the number of labels.
        """
        yield self.null_value
        yield from self.label_values
        yield self.num_values
    @property
    def declaration(self):
        """Return the enum type declaration as a string."""
        decl = self.type_specifier + ' {'
        for (idx, label) in enumerate(self.labels):
            decl += '\n\t' + f'{label} = {idx - 1},'
        decl = decl.rstrip(',')
        decl += '\n};'
        return decl

class Struct(Type):
    """C structures.

    - `prefix` is a string prefix for the type-specifier and typedef-name

    Reference: K&R ANSI C Section A8.3
    """
    def __init__(self, prefix):
        super().__init__(prefix)
        self._members = []
    @property
    def type_specifier(self):
        return f'struct {self._prefix}_tag'
    @property
    def typedef_name(self):
        return f'{self._prefix}_t'
    @property
    def opaque_type(self):
        raise NotImplementedError
    def append(self, declarator):
        """Append `declarator` to this instance's members."""
        self._members.append(declarator)
    def extend(self, declarators):
        """Extend `declarators` to this instance's members."""
        self._members.extend(declarators)
    @property
    def members(self):
        """Yield each declarator in this instance's members."""
        yield from self._members
    @property
    def declaration(self):
        """Return the struct type declaration as a string."""
        decl = self.type_specifier
        decl += ' {'
        for member in self.members:
            decl += '\n\t' + str(member) + ';'
        decl += '\n};'
        return decl

class Function():
    """C functions.

    - `identifier` is a string
    - `type_` is an instance of :class:`Type`
    - `storage_class` is a string specifying the storage class
      (K&R ANSI C Section A4.1)
    - `statements` is an iterable of implementation statements

    Reference: K&R ANSI C Section A10.1
    """
    def __init__(self, identifier, type_, storage_class=None, statements=()):
        self._identifier = identifier
        self._type = type_
        self._storage_class = storage_class
        self._statements = list(statements)
    @property
    def identifier(self):
        """Return this instance's identifier string."""
        return self._identifier
    @property
    def type_(self):
        """Return this instance's type object."""
        return self._type
    def append(self, statement):
        """Append `statement` to this instance's statements."""
        self._statements.append(statement)
    def extend(self, statements):
        """Extend `statements` to this instance's statements."""
        self._statements.extend(statements)
    @property
    def prototype(self):
        """Return the function prototype as a string."""
        storage_class = self._storage_class if self._storage_class else 'extern'
        return f'{storage_class} {self._type.interface(self._identifier)};'
    @property
    def implementation(self):
        """Return the function implementation as a string."""
        impl = self._storage_class + ' ' if self._storage_class else ''
        impl += self._type.interface(self._identifier)
        impl += ' {'
        for stmt in self._statements:
            for subs in str(stmt).split('\n'):
                impl += '\n\t' + subs
        impl += '\n}'
        return impl

class Array():
    """C arrays.

    - `identifier` is a string
    - `type_` is an instance of :class:`Type`
    - `storage_class` is a string specifying the storage class
      (K&R ANSI C Section A4.1)
    - `dimension` is a value defining the number of elements in the array
    - `elements` is an iterable of the array element values

    Reference: K&R ANSI C Section A8.6.2, A8.7
    """
    def __init__(
            self, identifier, type_,
            storage_class=None, dimension=None, elements=(),
        ): # pylint: disable=too-many-arguments
        self._identifier = identifier
        self._type = type_
        self._storage_class = storage_class
        self._dimension = dimension
        self._elements = list(elements)
    @property
    def identifier(self):
        """Return this instance's identifier string."""
        return self._identifier
    def append(self, element):
        """Append `element` to this instance's elements."""
        self._elements.append(element)
    def extend(self, elements):
        """Extend `elements` to this instance's elements."""
        self._elements.extend(elements)
    @property
    def implementation(self):
        """Return the array implementation as a string."""
        dimension = str(self._dimension) if self._dimension else ''
        impl = (self._storage_class + ' ') if self._storage_class else ''
        impl += self._type.typedef_name + ' '
        impl += self._identifier + '[' + dimension + '] = {'
        for elem in self._elements:
            impl += '\n\t' + elem + ','
        impl += '\n};'
        return impl

class Implementation(): # pylint: disable=too-many-instance-attributes
    """An instance of this class is a FSM implemented in C.

    The string representation is the C header and source code implementation.
    """
    def __init__(self, prefix): # pylint: disable=too-many-locals
        self._prefix = prefix
        ### C types
        type_state = Enum('state')
        type_event = Enum('event')
        type_condition = FunctionType('condition', 'int')
        type_action = FunctionType('action')
        type_fsm_cb = Struct(f'{prefix}_cb')
        type_fsm = Struct(prefix)
        type_init = FunctionType('init')
        type_inject = FunctionType('inject')
        ### C functions
        fn_init = Function(f'{prefix}_init', type_init)
        fn_not_handled = Function('not_handled', type_inject, 'static')
        ### complete all parts which do not depend upon FSM details
        decl_data = IndirectDeclarator('data')
        decl_arg = IndirectDeclarator('arg')
        ptr_fsm = type_fsm.pointer('fsm')
        ptr_fsm_cb = type_fsm_cb.pointer('cb')
        var_state = type_state.variable('state', opaque=True)
        ### complete types which do not depend upon FSM details
        type_condition.extend([ptr_fsm, decl_arg])
        type_action.extend([ptr_fsm, decl_arg])
        type_fsm.extend([ptr_fsm_cb, decl_data, var_state])
        type_init.extend([ptr_fsm, ptr_fsm_cb, decl_data, decl_arg])
        type_inject.extend([ptr_fsm, decl_arg])
        ### add statements which do not depend upon FSM details
        fn_not_handled.append(Comment('empty'))
        for decl in type_fsm.members:
            param = fn_init.type_.parameter(decl)
            if param:
                stmt = f'fsm->{decl.identifier} = {param.identifier};'
                fn_init.append(stmt)
        ### FSM types
        self._type_state = type_state
        self._type_event = type_event
        self._type_condition = type_condition
        self._type_action = type_action
        self._type_fsm_cb = type_fsm_cb
        self._type_fsm = type_fsm
        self._type_init = type_init
        self._type_inject = type_inject
        ### FSM functions
        self._fn_init = fn_init
        self._fn_not_handled = fn_not_handled
        self._fn_event_handlers = []
        self._arrays_event_handlers = []
        self._fn_event_injectors = []
    def declare_state(self, state):
        """Declare `state` label in this FSM's state enumeration."""
        self._type_state.append(state)
    def declare_event(self, event):
        """Declare `event` name in this FSM's event enumeration.

        Create an array for transition event handlers, one per state.
        Create a function for injecting event: the transition event handler for
        the current state will be invoked.
        """
        ### add to enum
        self._type_event.append(event)
        ### create array
        arr_name = f'transition_on_event_{event}'
        dimension = self._type_state.num_values
        array = Array(arr_name, self._type_inject, 'static', dimension)
        self._arrays_event_handlers.append(array)
        ### create function
        fn_name = f'{self._prefix}_inject_{event}'
        injector = Function(fn_name, self._type_inject)
        protect = f'(0 <= fsm->state) && (fsm->state < {dimension})'
        inject = f'{array.identifier}[fsm->state](fsm, arg);'
        injector.append(IfCondition(protect, [inject]))
        self._fn_event_injectors.append(injector)
    def declare_condition(self, condition):
        """Declare `condition` name as a callback function for this FSM."""
        fn_name = f'condition_{condition}'
        decl = IndirectDeclarator(fn_name, self._type_condition)
        self._type_fsm_cb.append(decl)
    def declare_action(self, action):
        """Declare `action` name as a callback function for this FSM."""
        fn_name = f'action_{action}'
        decl = IndirectDeclarator(fn_name, self._type_action)
        self._type_fsm_cb.append(decl)
    def _step_to_statements(self, step):
        """Transform transition `step` into executable C statements.

        If `step` specifies a list of 'actions' then call each callback action
        in turn. If `step` specifies a next 'state' then set the FSM state to
        the label for that state.
        """
        stmts = []
        try:
            actions = step['actions']
        except KeyError:
            pass
        else:
            stmts += [f'fsm->cb->action_{a}(fsm, arg);' for a in actions]
        try:
            next_state = step['state']
        except KeyError:
            pass
        else:
            if next_state:
                label = self._type_state.label_value(next_state)
            else:
                label = self._type_state.null_value
            stmts.append(f'fsm->state = {label};')
        return stmts
    def define_init_handler(self, transition):
        """Extend the FSM init function with the initial `transition` steps."""
        stmts = []
        for step in transition['steps']:
            stmts += self._step_to_statements(step)
        self._fn_init.extend(stmts)
    def define_handler(self, event, state, transitions):
        """Define the handler function for handling `event` in `state`.

        If `transitions` does not define steps for handling `event` in `state`,
        then register the unhandled event function. Otherwise, create and
        register a new function implementing the transition steps.
        """
        stmts = []
        for transition in transitions:
            block = []
            for step in transition['steps']:
                block += self._step_to_statements(step)
            condition = transition['condition']
            if condition:
                c_expr = f'fsm->cb->condition_{condition}(fsm, arg)'
                block.append('return;')
                taken = transition['taken']
                stmts.append(IfCondition(c_expr, block, taken))
            else:
                stmts += block
        if stmts:
            name = f'handle_{event}_in_{state}'
            handler = Function(name, self._type_inject, 'static', stmts)
            self._fn_event_handlers.append(handler)
            fn_identifier = handler.identifier
        else:
            fn_identifier = self._fn_not_handled.identifier
        array = self._arrays_event_handlers[self._type_event.index(event)]
        array.append(fn_identifier)
    @property
    def eof(self):
        """Return a single line end-of-file comment."""
        return str(Comment('EOF'))
    @property
    def header(self):
        """Return the C header implementation of this FSM as a string."""
        return '\n'.join([
            self._type_fsm.typedef,
            self._type_fsm_cb.typedef,
            '',
            self._type_condition.typedef,
            self._type_action.typedef,
            '',
            self._type_fsm_cb.declaration,
            '',
            self._type_fsm.declaration,
            '',
            self._fn_init.prototype,
        ] + [
            fn.prototype for fn in self._fn_event_injectors
        ] + [
            '',
            self.eof,
        ])
    @property
    def source(self):
        """Return the C source implementation of this FSM as a string."""
        return '\n'.join([
            self._type_state.typedef,
            self._type_event.typedef,
            '',
            self._type_state.declaration,
            '',
            self._type_event.declaration,
            '',
            self._type_inject.typedef,
            '',
            self._fn_not_handled.implementation,
            '',
        ] + [
            fn.implementation for fn in self._fn_event_handlers
        ] + [
            '',
        ] + [
            array.implementation for array in self._arrays_event_handlers
        ] + [
            '',
            self._fn_init.implementation,
        ] + [
            fn.implementation for fn in self._fn_event_injectors
        ] + [
            '',
            self.eof,
        ])
    def __str__(self):
        """Return the C header and C source implementations."""
        return self.header + '\n' + self.source

class Builder(_Builder):
    """A builder for target implementation of a FSM in C."""
    def pointer_to_state_label(self, pointer):
        """Return a label for a state from absolute state `pointer`."""
        return '_'.join(self.pointer_to_path(pointer))
    def fix_steps(self, transition):
        """Fix `transition` steps state pointers to state labels.

        Replace each state pointer in `transition` steps with its state label.
        """
        for step in transition['steps']:
            try:
                pointer = step['state']
            except KeyError:
                continue
            if pointer:
                step['state'] = self.pointer_to_state_label(pointer)
            else:
                step['state'] = None
        return transition
    def _get_initial_transition(self):
        """Return the initial transition for this FSM.

        Replace each state pointer in the initial transition steps with its
        state label.
        """
        return self.fix_steps(self.get_initial_transition())
    def _get_transitions(self, event, pointer):
        """Return a list of transitions for handling `event` in the given state.

        Return a list of transitions for handling `event` in the state pointed
        to by absolute state `pointer`, with each state pointer in the
        transition steps replaced with its state label.
        """
        return [self.fix_steps(_) for _ in self.get_transitions(event, pointer)]
    def build_implementation(self):
        impl = Implementation(f'{self._prefix}_fsm')
        states = sorted(self.states)
        events = sorted(self.events)
        conditions = sorted(self.conditions)
        actions = sorted(self.actions)
        for pointer in states:
            impl.declare_state(self.pointer_to_state_label(pointer))
        for name in events:
            impl.declare_event(name)
        for name in conditions:
            impl.declare_condition(name)
        for name in actions:
            impl.declare_action(name)
        transition = self._get_initial_transition()
        impl.define_init_handler(transition)
        for event in events:
            for pointer in states:
                label = self.pointer_to_state_label(pointer)
                transitions = self._get_transitions(event, pointer)
                impl.define_handler(event, label, transitions)
        return impl
