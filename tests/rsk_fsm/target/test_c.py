### SPDX-License-Identifier: GPL-2.0-or-later

"""Test cases for rsk_fsm.target.c"""

from unittest import TestCase
from nose2.tools import params

from rsk_fsm.target.c import (
    Comment,
    IfCondition,
    Declarator,
    IndirectDeclarator,
    Type,
    FunctionType,
    Enum,
    Struct,
    Function,
    Array,
)

from .. import make_fqname

class _TestBuilder(type):
    """Build tests for rsk_fsm.target.c.* test cases

    Specify this class as metaclass and provide:
    `constructor` - the class under test
    `stringify` - a sequence of (constructor args, string representation) pairs
    `attrs` - a sequence of (constructor args, attr name, attr value) triplets
    """
    def __new__(cls, name, bases, dct):
        constructor = dct['constructor']
        fqname = make_fqname(constructor)
        try:
            method = cls.make_test_stringify(
                constructor, fqname,
                dct['stringify'],
            )
            dct['test_stringify'] = method
        except KeyError:
            pass
        try:
            method = cls.make_test_attrs(
                constructor, fqname,
                dct['attrs'],
            )
            dct['test_attrs'] = method
        except KeyError:
            pass
        return super().__new__(cls, name, bases, dct)
    @staticmethod
    def make_test_stringify(constructor, fqname, pairs):
        """Make a function testing stringifying a class instance"""
        @params(*pairs)
        def method(self, cargs, string):
            """Test object constructed with `cargs` stringifies to `string`"""
            obj = constructor(*cargs)
            self.assertEqual(str(obj), string)
        method.__doc__ = f'Test {fqname} stringify'
        return method
    @staticmethod
    def make_test_attrs(constructor, fqname, triplets):
        """Make a function testing class instance attribute value"""
        @params(*triplets)
        def method(self, cargs, attr, val):
            """Test object constructed with `cargs` has `attr` with `val`"""
            obj = constructor(*cargs)
            self.assertEqual(getattr(obj, attr), val)
        method.__doc__ = f'Test {fqname} attribute values'
        return method

class TestComment(TestCase, metaclass=_TestBuilder):
    """Test cases for rsk_fsm.target.c.Comment."""
    constructor = Comment
    stringify = (
        (
            ['single line comment',],
            '/* single line comment */',
        ),
        (
            ['single line comment trailing whitespace\t \n    ',],
            '/* single line comment trailing whitespace */',
        ),
        (
            ['multi\nline\ncomment\n',],
            '/* multi\n * line\n * comment\n */',
        ),
    )

class TestIfCondition(TestCase, metaclass=_TestBuilder):
    """Test cases for rsk_fsm.target.c.IfCondition."""
    constructor = IfCondition
    stringify = (
        (
            ['foo', ['bar = baz;', 'baz += 2;']],
            'if (foo) {\n\tbar = baz;\n\tbaz += 2;\n}',
        ),
        (
            ['foo', ['bar = baz;'], False],
            'if (!(foo)) {\n\tbar = baz;\n}',
        ),
    )

class TestDeclarator(TestCase, metaclass=_TestBuilder):
    """Test cases for rsk_fsm.target.c.Declarator."""
    constructor = Declarator
    quux = Enum('quux')
    stringify = (
        (
            [],
            'void',
        ),
        (
            ['foo'],
            'void foo',
        ),
        (
            ['bar', None, 'int'],
            'int bar',
        ),
        (
            ['baz', quux],
            'quux_e baz',
        ),
        (
            ['wibble', quux, 'corge'],
            'corge wibble',
        ),
    )
    attrs = (
        (
            [],
            'identifier',
            None,
        ),
        (
            [],
            'type_',
            None,
        ),
        (
            ['foo'],
            'identifier',
            'foo',
        ),
        (
            ['foo'],
            'type_',
            None,
        ),
        (
            ['bar', None, 'int'],
            'identifier',
            'bar',
        ),
        (
            ['bar', None, 'int'],
            'type_',
            None,
        ),
        (
            ['baz', quux],
            'identifier',
            'baz',
        ),
        (
            ['baz', quux],
            'type_',
            quux,
        ),
        (
            ['wibble', quux, 'corge'],
            'identifier',
            'wibble',
        ),
        (
            ['wibble', quux, 'corge'],
            'type_',
            quux,
        ),
    )
    @params(
        (Declarator('foo'), Declarator('foo'), True),
        (Declarator('foo'), Declarator('bar'), False),
        (Declarator('bar'), Declarator('foo'), False),
        (Declarator('foo', quux), Declarator('foo', quux), True),
        (Declarator('foo'), Declarator('foo', quux), False),
        (Declarator('foo', quux), Declarator('foo'), False),
    )
    def test_eq(self, val1, val2, equal):
        """Test rsk_fsm.target.c.Declarator value equality"""
        if equal:
            self.assertTrue(val1 == val2)
        else:
            self.assertFalse(val1 == val2)

class TestIndirectDeclarator(TestCase, metaclass=_TestBuilder):
    """Test cases for rsk_fsm.target.c.IndirectDeclarator."""
    constructor = IndirectDeclarator
    quuz = Struct('quuz')
    stringify = (
        (
            ['foo'],
            'void * foo',
        ),
        (
            ['bar', None, 'int'],
            'int * bar',
        ),
        (
            ['baz', quuz],
            'quuz_t * baz',
        ),
        (
            ['wibble', quuz, 'corge'],
            'quuz_t * wibble',
        ),
    )
    attrs = (
        (
            ['foo'],
            'identifier',
            'foo',
        ),
        (
            ['foo'],
            'type_',
            None,
        ),
        (
            ['bar', None, 'int'],
            'identifier',
            'bar',
        ),
        (
            ['bar', None, 'int'],
            'type_',
            None,
        ),
        (
            ['baz', quuz],
            'identifier',
            'baz',
        ),
        (
            ['baz', quuz],
            'type_',
            quuz,
        ),
        (
            ['wibble', quuz, 'corge'],
            'identifier',
            'wibble',
        ),
        (
            ['wibble', quuz, 'corge'],
            'type_',
            quuz,
        ),
    )
    @params(
        (IndirectDeclarator('foo'), IndirectDeclarator('foo'), True),
        (IndirectDeclarator('foo'), IndirectDeclarator('bar'), False),
        (IndirectDeclarator('bar'), IndirectDeclarator('foo'), False),
        (IndirectDeclarator('foo', quuz), IndirectDeclarator('foo', quuz), True),
        (IndirectDeclarator('foo'), IndirectDeclarator('foo', quuz), False),
        (IndirectDeclarator('foo', quuz), IndirectDeclarator('foo'), False),
        (IndirectDeclarator('foo'), Declarator('foo'), False),
        (Declarator('foo'), IndirectDeclarator('foo'), False),
    )
    def test_eq(self, val1, val2, equal):
        """Test rsk_fsm.target.c.IndirectDeclarator value equality"""
        if equal:
            self.assertTrue(val1 == val2)
        else:
            self.assertFalse(val1 == val2)

class TestType(TestCase, metaclass=_TestBuilder):
    """Test cases for rsk_fsm.target.c.Type."""
    constructor = Type
    def test_str(self):
        """Test rsk_fsm.target.c.Type.__str__ is abstract"""
        with self.assertRaises(NotImplementedError):
            str(self.constructor('foo'))
    def test_type_specifier(self):
        """Test rsk_fsm.target.c.Type.type_specifier is abstract"""
        with self.assertRaises(NotImplementedError):
            # pylint: disable=expression-not-assigned
            self.constructor('foo').type_specifier
    def test_typedef_name(self):
        """Test rsk_fsm.target.c.Type.typedef_name is abstract"""
        with self.assertRaises(NotImplementedError):
            # pylint: disable=expression-not-assigned
            self.constructor('foo').typedef_name
    def test_typedef(self):
        """Test rsk_fsm.target.c.Type.typedef is abstract"""
        with self.assertRaises(NotImplementedError):
            # pylint: disable=expression-not-assigned
            self.constructor('foo').typedef
    def test_type_pointer(self):
        """Test rsk_fsm.target.c.Type.type_pointer is abstract"""
        with self.assertRaises(NotImplementedError):
            # pylint: disable=expression-not-assigned
            self.constructor('foo').type_pointer
    def test_opaque_type(self):
        """Test rsk_fsm.target.c.Type.opaque_type is abstract"""
        with self.assertRaises(NotImplementedError):
            # pylint: disable=expression-not-assigned
            self.constructor('foo').opaque_type
    def test_null_value(self):
        """Test rsk_fsm.target.c.Type.null_value"""
        self.assertEqual(self.constructor('foo').null_value, 0)
    def test_pointer(self):
        """Test rsk_fsm.target.c.Type.pointer is abstract"""
        with self.assertRaises(NotImplementedError):
            self.constructor('foo').pointer('bar')
    def test_variable(self):
        """Test rsk_fsm.target.c.Type.variable is abstract"""
        with self.assertRaises(NotImplementedError):
            self.constructor('foo').variable('bar')
    def test_variable_opaque(self):
        """Test rsk_fsm.target.c.Type.variable (opaque) is abstract"""
        with self.assertRaises(NotImplementedError):
            self.constructor('foo').variable('bar', True)

class TestFunctionType(TestCase, metaclass=_TestBuilder):
    """Test cases for rsk_fsm.target.c.FunctionType."""
    constructor = FunctionType
    def test_type_specifier(self):
        """Test rsk_fsm.target.c.FunctionType.type_specifier is abstract"""
        with self.assertRaises(NotImplementedError):
            # pylint: disable=expression-not-assigned
            self.constructor('foo').type_specifier
    def test_typedef_name(self):
        """Test rsk_fsm.target.c.FunctionType.typedef_name"""
        instance = self.constructor('foo')
        self.assertEqual(instance.typedef_name, 'foo_fp')
        self.assertEqual(instance.typedef_name, str(instance))
    def test_typedef(self):
        """Test rsk_fsm.target.c.FunctionType.typedef"""
        self.assertEqual(
            self.constructor('foo').typedef,
            'typedef void (*foo_fp)(void);',
        )
        self.assertEqual(
            self.constructor('bar', 'int').typedef,
            'typedef int (*bar_fp)(void);',
        )
        parameters = (
            Declarator('quuz', None, 'quux_t'),
            IndirectDeclarator('wibble', Struct('corge')),
        )
        self.assertEqual(
            self.constructor('baz', None, parameters).typedef,
            'typedef void (*baz_fp)(quux_t quuz, corge_t * wibble);',
        )
    def test_type_pointer(self):
        """Test rsk_fsm.target.c.FunctionType.type_pointer"""
        self.assertEqual(self.constructor('foo').type_pointer, 'foo_fp')
    def test_opaque_type(self):
        """Test rsk_fsm.target.c.FunctionType.opaque_type is abstract"""
        with self.assertRaises(NotImplementedError):
            # pylint: disable=expression-not-assigned
            self.constructor('foo').opaque_type
    def test_null_value(self):
        """Test rsk_fsm.target.c.FunctionType.null_value"""
        self.assertEqual(self.constructor('foo').null_value, 0)
    def test_pointer(self):
        """Test rsk_fsm.target.c.FunctionType.pointer"""
        instance = self.constructor('foo')
        self.assertEqual(
            instance.pointer('bar'),
            IndirectDeclarator('bar', instance),
        )
    def test_variable(self):
        """Test rsk_fsm.target.c.FunctionType.variable"""
        instance = self.constructor('foo')
        self.assertEqual(
            instance.variable('bar'),
            Declarator('bar', instance),
        )
    def test_variable_opaque(self):
        """Test rsk_fsm.target.c.FunctionType.variable (opaque) is abstract"""
        with self.assertRaises(NotImplementedError):
            self.constructor('foo').variable('bar', True)
    def test_parameters(self):
        """Test rsk_fsm.target.c.FunctionType.parameters"""
        instance = self.constructor('foo')
        self.assertEqual(
            list(instance.parameters),
            [Declarator()],
        )
        self.assertIsNone(instance.append(IndirectDeclarator('bar')))
        self.assertEqual(
            list(instance.parameters),
            [IndirectDeclarator('bar')],
        )
        quuz = Struct('quuz')
        dst = IndirectDeclarator('dst', quuz)
        self.assertIsNone(
            instance.extend((dst, IndirectDeclarator('src', quuz))),
        )
        self.assertEqual(
            list(instance.parameters),
            [
                IndirectDeclarator('bar'),
                IndirectDeclarator('dst', quuz),
                IndirectDeclarator('src', quuz),
            ],
        )
        self.assertIsNone(
            instance.parameter(Declarator()),
        )
        self.assertEqual(
            instance.parameter(IndirectDeclarator('dst', quuz)),
            dst,
        )
    def test_interface(self):
        """Test rsk_fsm.target.c.FunctionType.interface"""
        instance = self.constructor('foo', 'int', (
            Declarator('a', None, 'int'),
            Declarator('b', None, 'int'),
            Declarator('c', None, 'int'),
        ))
        self.assertEqual(
            instance.interface('sum'),
            'int sum(int a, int b, int c)',
        )

class TestEnum(TestCase, metaclass=_TestBuilder):
    """Test cases for rsk_fsm.target.c.Enum."""
    constructor = Enum
    def test_type_specifier(self):
        """Test rsk_fsm.target.c.Enum.type_specifier"""
        self.assertEqual(
            self.constructor('foo').type_specifier,
            'enum foo_tag',
        )
    def test_typedef_name(self):
        """Test rsk_fsm.target.c.Enum.typedef_name"""
        instance = self.constructor('foo')
        self.assertEqual(instance.typedef_name, 'foo_e')
        self.assertEqual(instance.typedef_name, str(instance))
    def test_typedef(self):
        """Test rsk_fsm.target.c.Enum.typedef"""
        self.assertEqual(
            self.constructor('foo').typedef,
            'typedef enum foo_tag foo_e;',
        )
    def test_type_pointer(self):
        """Test rsk_fsm.target.c.Enum.type_pointer"""
        self.assertEqual(
            self.constructor('foo').type_pointer,
            'foo_e *',
        )
    def test_opaque_type(self):
        """Test rsk_fsm.target.c.Enum.opaque_type"""
        self.assertEqual(
            self.constructor('foo').opaque_type,
            'int',
        )
    def test_null_value(self):
        """Test rsk_fsm.target.c.Enum.null_value"""
        self.assertEqual(
            self.constructor('foo').null_value,
            'INVALID_FOO',
        )
    def test_pointer(self):
        """Test rsk_fsm.target.c.Enum.pointer"""
        instance = self.constructor('foo')
        self.assertEqual(
            instance.pointer('bar'),
            IndirectDeclarator('bar', instance),
        )
    def test_variable(self):
        """Test rsk_fsm.target.c.Enum.variable"""
        instance = self.constructor('foo')
        self.assertEqual(
            instance.variable('bar'),
            Declarator('bar', instance),
        )
    def test_variable_opaque(self):
        """Test rsk_fsm.target.c.Enum.variable (opaque)"""
        instance = self.constructor('foo')
        self.assertEqual(
            instance.variable('bar', True),
            Declarator('bar', instance),
        )
        self.assertEqual(
            str(instance.variable('bar', True)),
            'int bar',
        )
    def test_label_unknown(self):
        """Test rsk_fsm.target.c.Enum.label_value rejects unknown label"""
        with self.assertRaises(ValueError):
            self.constructor('foo').label_value('bar')
    def test_labels(self):
        """Test rsk_fsm.target.c.Enum.labels"""
        instance = self.constructor('foo')
        self.assertEqual(
            instance.append('bar'),
            None,
        )
        self.assertEqual(
            instance.extend(('baz', 'quuz', 'quux')),
            None,
        )
        self.assertEqual(instance.index('bar'), 0)
        self.assertEqual(instance.index('baz'), 1)
        self.assertEqual(instance.index('quuz'), 2)
        self.assertEqual(instance.index('quux'), 3)
        self.assertEqual(
            list(instance.labels),
            [
                'INVALID_FOO',
                'FOO_BAR',
                'FOO_BAZ',
                'FOO_QUUZ',
                'FOO_QUUX',
                'NUM_FOO',
            ],
        )
    def test_declaration(self):
        """Test rsk_fsm.target.c.Enum.declaration"""
        instance = self.constructor('foo')
        self.assertEqual(
            instance.extend(('bar', 'baz')),
            None,
        )
        self.assertEqual(
            instance.declaration,
            '\n'.join([
                'enum foo_tag {',
                '\tINVALID_FOO = -1,',
                '\tFOO_BAR = 0,',
                '\tFOO_BAZ = 1,',
                '\tNUM_FOO = 2',
                '};',
            ]),
        )

class TestStruct(TestCase, metaclass=_TestBuilder):
    """Test cases for rsk_fsm.target.c.Struct."""
    constructor = Struct
    def test_type_specifier(self):
        """Test rsk_fsm.target.c.Struct.type_specifier"""
        self.assertEqual(
            self.constructor('foo').type_specifier,
            'struct foo_tag',
        )
    def test_typedef_name(self):
        """Test rsk_fsm.target.c.Struct.typedef_name"""
        instance = self.constructor('foo')
        self.assertEqual(instance.typedef_name, 'foo_t')
        self.assertEqual(instance.typedef_name, str(instance))
    def test_typedef(self):
        """Test rsk_fsm.target.c.Struct.typedef"""
        self.assertEqual(
            self.constructor('foo').typedef,
            'typedef struct foo_tag foo_t;',
        )
    def test_type_pointer(self):
        """Test rsk_fsm.target.c.Struct.type_pointer"""
        self.assertEqual(
            self.constructor('foo').type_pointer,
            'foo_t *',
        )
    def test_opaque_type(self):
        """Test rsk_fsm.target.c.Struct.opaque_type is abstract"""
        with self.assertRaises(NotImplementedError):
            # pylint: disable=expression-not-assigned
            self.constructor('foo').opaque_type
    def test_null_value(self):
        """Test rsk_fsm.target.c.Struct.null_value"""
        self.assertEqual(self.constructor('foo').null_value, 0)
    def test_pointer(self):
        """Test rsk_fsm.target.c.Struct.pointer"""
        instance = self.constructor('foo')
        self.assertEqual(
            instance.pointer('bar'),
            IndirectDeclarator('bar', instance),
        )
    def test_variable(self):
        """Test rsk_fsm.target.c.Struct.variable"""
        instance = self.constructor('foo')
        self.assertEqual(
            instance.variable('bar'),
            Declarator('bar', instance),
        )
    def test_variable_opaque(self):
        """Test rsk_fsm.target.c.Struct.variable (opaque)"""
        with self.assertRaises(NotImplementedError):
            self.constructor('foo').variable('bar', True)
    def test_members(self):
        """Test rsk_fsm.target.c.Struct.members"""
        instance = self.constructor('foo')
        self.assertIsNone(instance.append(IndirectDeclarator('base')))
        self.assertIsNone(instance.extend((Declarator('count', None, 'int'),)))
        self.assertEqual(
            list(instance.members),
            [
                IndirectDeclarator('base'),
                Declarator('count', None, 'int'),
            ],
        )
    def test_declaration(self):
        """Test rsk_fsm.target.c.Struct.declaration"""
        instance = self.constructor('foo')
        self.assertIsNone(instance.append(IndirectDeclarator('base')))
        self.assertIsNone(instance.append(Declarator('count', None, 'int')))
        self.assertEqual(
            instance.declaration,
            '\n'.join([
                'struct foo_tag {',
                '\tvoid * base;',
                '\tint count;',
                '};',
            ]),
        )

class TestFunction(TestCase, metaclass=_TestBuilder):
    """Test cases for rsk_fsm.target.c.Function"""
    constructor = Function
    quuz = FunctionType('quuz', 'int')
    attrs = (
        (
            ['foo', quuz, 'static'],
            'identifier',
            'foo',
        ),
        (
            ['foo', quuz, 'static'],
            'type_',
            quuz,
        ),
    )
    def test_implementation(self):
        """Test rsk_fsm.target.c.Function.implementation"""
        instance = self.constructor(
            'foo', self.quuz, 'static', [Comment('begin')],
        )
        self.assertIsNone(instance.append('statement 1'))
        self.assertIsNone(instance.extend(('statement 2', Comment('end'))))
        self.assertEqual(
            instance.prototype,
            'static int foo(void);',
        )
        self.assertEqual(
            instance.implementation,
            '\n'.join([
                'static int foo(void) {',
                '\t/* begin */',
                '\tstatement 1',
                '\tstatement 2',
                '\t/* end */',
                '}',
            ]),
        )

class TestArray(TestCase, metaclass=_TestBuilder):
    """Test cases for rsk_fsm.target.c.Array"""
    constructor = Array
    quuz = FunctionType('quuz', 'int')
    attrs = (
        (
            ['foo', quuz],
            'identifier',
            'foo',
        ),
    )
    def test_implementation(self):
        """Test rsk_fsm.target.c.Array.implementation"""
        instance = self.constructor('foo', self.quuz, dimension=3)
        self.assertIsNone(instance.append('bar'))
        self.assertIsNone(instance.extend(('baz', 'quux')))
        self.assertEqual(
            instance.implementation,
            '\n'.join([
                'quuz_fp foo[3] = {',
                '\tbar,',
                '\tbaz,',
                '\tquux,',
                '};',
            ]),
        )
