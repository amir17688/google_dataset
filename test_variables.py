import json

from pytest import raises

from graphql.core.error import GraphQLError, format_error
from graphql.core.execution import execute
from graphql.core.language.parser import parse
from graphql.core.type import (GraphQLArgument, GraphQLField,
                               GraphQLInputObjectField, GraphQLInputObjectType,
                               GraphQLList, GraphQLNonNull, GraphQLObjectType,
                               GraphQLScalarType, GraphQLSchema, GraphQLString)

TestComplexScalar = GraphQLScalarType(
    name='ComplexScalar',
    serialize=lambda v: 'SerializedValue' if v == 'DeserializedValue' else None,
    parse_value=lambda v: 'DeserializedValue' if v == 'SerializedValue' else None,
    parse_literal=lambda v: 'DeserializedValue' if v.value == 'SerializedValue' else None
)

TestInputObject = GraphQLInputObjectType('TestInputObject', {
    'a': GraphQLInputObjectField(GraphQLString),
    'b': GraphQLInputObjectField(GraphQLList(GraphQLString)),
    'c': GraphQLInputObjectField(GraphQLNonNull(GraphQLString)),
    'd': GraphQLInputObjectField(TestComplexScalar)
})

stringify = lambda obj: json.dumps(obj, sort_keys=True)


def input_to_json(obj, args, info):
    input = args.get('input')
    if input:
        return stringify(input)


TestNestedInputObject = GraphQLInputObjectType(
    name='TestNestedInputObject',
    fields={
        'na': GraphQLInputObjectField(GraphQLNonNull(TestInputObject)),
        'nb': GraphQLInputObjectField(GraphQLNonNull(GraphQLString))
    }
)

TestType = GraphQLObjectType('TestType', {
    'fieldWithObjectInput': GraphQLField(
        GraphQLString,
        args={'input': GraphQLArgument(TestInputObject)},
        resolver=input_to_json),
    'fieldWithNullableStringInput': GraphQLField(
        GraphQLString,
        args={'input': GraphQLArgument(GraphQLString)},
        resolver=input_to_json),
    'fieldWithNonNullableStringInput': GraphQLField(
        GraphQLString,
        args={'input': GraphQLArgument(GraphQLNonNull(GraphQLString))},
        resolver=input_to_json),
    'fieldWithDefaultArgumentValue': GraphQLField(
        GraphQLString,
        args={'input': GraphQLArgument(GraphQLString, 'Hello World')},
        resolver=input_to_json),
    'fieldWithNestedInputObject': GraphQLField(
        GraphQLString,
        args={'input': GraphQLArgument(TestNestedInputObject, 'Hello World')},
        resolver=input_to_json),
    'list': GraphQLField(
        GraphQLString,
        args={'input': GraphQLArgument(GraphQLList(GraphQLString))},
        resolver=input_to_json),
    'nnList': GraphQLField(
        GraphQLString,
        args={'input': GraphQLArgument(
            GraphQLNonNull(GraphQLList(GraphQLString))
        )},
        resolver=input_to_json),
    'listNN': GraphQLField(
        GraphQLString,
        args={'input': GraphQLArgument(
            GraphQLList(GraphQLNonNull(GraphQLString))
        )},
        resolver=input_to_json),
    'nnListNN': GraphQLField(
        GraphQLString,
        args={'input': GraphQLArgument(
            GraphQLNonNull(GraphQLList(GraphQLNonNull(GraphQLString)))
        )},
        resolver=input_to_json),
})

schema = GraphQLSchema(TestType)


def check(doc, expected, args=None):
    ast = parse(doc)
    response = execute(schema, None, ast, args=args)

    if response.errors:
        result = {
            'data': response.data,
            'errors': [format_error(e) for e in response.errors]
        }
    else:
        result = {
            'data': response.data
        }

    assert result == expected


# Handles objects and nullability

def test_inline_executes_with_complex_input():
    doc = '''
    {
      fieldWithObjectInput(input: {a: "foo", b: ["bar"], c: "baz"})
    }
    '''
    check(doc, {
        'data': {"fieldWithObjectInput": stringify({"a": "foo", "b": ["bar"], "c": "baz"})}
    })


def test_properly_parses_single_value_to_list():
    doc = '''
    {
        fieldWithObjectInput(input: {a: "foo", b: "bar", c: "baz"})
    }
    '''
    check(doc, {
        'data': {'fieldWithObjectInput': stringify({"a": "foo", "b": ["bar"], "c": "baz"})}
    })


def test_does_not_use_incorrect_value():
    doc = '''
    {
        fieldWithObjectInput(input: ["foo", "bar", "baz"])
    }
    '''
    check(doc, {
        'data': {'fieldWithObjectInput': None}
    })


# noinspection PyMethodMayBeStatic
class TestUsingVariables:
    doc = '''
    query q($input: TestInputObject) {
      fieldWithObjectInput(input: $input)
    }
    '''

    def test_executes_with_complex_input(self):
        params = {'input': {'a': 'foo', 'b': ['bar'], 'c': 'baz'}}
        check(self.doc, {
            'data': {'fieldWithObjectInput': stringify({"a": "foo", "b": ["bar"], "c": "baz"})}
        }, params)

    def test_uses_default_value_when_not_provided(self):
        with_defaults_doc = '''
        query q($input: TestInputObject = {a: "foo", b: ["bar"], c: "baz"}) {
            fieldWithObjectInput(input: $input)
        }
        '''

        check(with_defaults_doc, {
            'data': {'fieldWithObjectInput': stringify({"a": "foo", "b": ["bar"], "c": "baz"})}
        })

    def test_properly_parses_single_value_to_list(self):
        params = {'input': {'a': 'foo', 'b': 'bar', 'c': 'baz'}}
        check(self.doc, {
            'data': {'fieldWithObjectInput': stringify({"a": "foo", "b": ["bar"], "c": "baz"})}
        }, params)

    def test_executes_with_complex_scalar_input(self):
        params = {'input': {'c': 'foo', 'd': 'SerializedValue'}}
        check(self.doc, {
            'data': {'fieldWithObjectInput': stringify({"c": "foo", "d": "DeserializedValue"})}
        }, params)

    def test_errors_on_null_for_nested_non_null(self):
        params = {'input': {'a': 'foo', 'b': 'bar', 'c': None}}

        with raises(GraphQLError) as excinfo:
            check(self.doc, {}, params)

        assert format_error(excinfo.value) == {
            'locations': [{'column': 13, 'line': 2}],
            'message': 'Variable "$input" got invalid value {}.\n'
                       'In field "c": Expected "String!", found null.'.format(stringify(params['input']))
        }

    def test_errors_on_incorrect_type(self):
        params = {'input': 'foo bar'}

        with raises(GraphQLError) as excinfo:
            check(self.doc, {}, params)

        assert format_error(excinfo.value) == {
            'locations': [{'column': 13, 'line': 2}],
            'message': 'Variable "$input" got invalid value {}.\n'
                       'Expected "TestInputObject", found not an object.'.format(stringify(params['input']))
        }

    def test_errors_on_omission_of_nested_non_null(self):
        params = {'input': {'a': 'foo', 'b': 'bar'}}

        with raises(GraphQLError) as excinfo:
            check(self.doc, {}, params)

        assert format_error(excinfo.value) == {
            'locations': [{'column': 13, 'line': 2}],
            'message': 'Variable "$input" got invalid value {}.\n'
                       'In field "c": Expected "String!", found null.'.format(stringify(params['input']))
        }

    def test_errors_on_deep_nested_errors_and_with_many_errors(self):
        nested_doc = '''
          query q($input: TestNestedInputObject) {
            fieldWithNestedObjectInput(input: $input)
          }
        '''

        params = {'input': {'na': {'a': 'foo'}}}
        with raises(GraphQLError) as excinfo:
            check(nested_doc, {}, params)

        assert format_error(excinfo.value) == {
            'locations': [{'column': 19, 'line': 2}],
            'message': 'Variable "$input" got invalid value {}.\n'
                       'In field "na": In field "c": Expected "String!", found null.\n'
                       'In field "nb": Expected "String!", found null.'.format(stringify(params['input']))
        }

    def test_errors_on_addition_of_input_field_of_incorrect_type(self):
        params = {'input': {'a': 'foo', 'b': 'bar', 'c': 'baz', 'd': 'dog'}}

        with raises(GraphQLError) as excinfo:
            check(self.doc, {}, params)

        assert format_error(excinfo.value) == {
            'locations': [{'column': 13, 'line': 2}],
            'message': 'Variable "$input" got invalid value {}.\n'
                       'In field "d": Expected type "ComplexScalar", found "dog".'.format(stringify(params['input']))
        }

    def test_errors_on_addition_of_unknown_input_field(self):
        params = {'input': {'a': 'foo', 'b': 'bar', 'c': 'baz', 'extra': 'dog'}}

        with raises(GraphQLError) as excinfo:
            check(self.doc, {}, params)

        assert format_error(excinfo.value) == {
            'locations': [{'column': 13, 'line': 2}],
            'message': 'Variable "$input" got invalid value {}.\n'
                       'In field "extra": Unknown field.'.format(stringify(params['input']))
        }


def test_allows_nullable_inputs_to_be_omitted():
    doc = '{ fieldWithNullableStringInput }'
    check(doc, {'data': {
        'fieldWithNullableStringInput': None
    }})


def test_allows_nullable_inputs_to_be_omitted_in_a_variable():
    doc = '''
    query SetsNullable($value: String) {
        fieldWithNullableStringInput(input: $value)
    }
    '''

    check(doc, {
        'data': {
            'fieldWithNullableStringInput': None
        }
    })


def test_allows_nullable_inputs_to_be_omitted_in_an_unlisted_variable():
    doc = '''
    query SetsNullable {
        fieldWithNullableStringInput(input: $value)
    }
    '''

    check(doc, {
        'data': {
            'fieldWithNullableStringInput': None
        }
    })


def test_allows_nullable_inputs_to_be_set_to_null_in_a_variable():
    doc = '''
    query SetsNullable($value: String) {
        fieldWithNullableStringInput(input: $value)
    }
    '''
    check(doc, {
        'data': {
            'fieldWithNullableStringInput': None
        }
    }, {'value': None})


def test_allows_nullable_inputs_to_be_set_to_a_value_in_a_variable():
    doc = '''
    query SetsNullable($value: String) {
        fieldWithNullableStringInput(input: $value)
    }
    '''

    check(doc, {
        'data': {
            'fieldWithNullableStringInput': '"a"'
        }
    }, {'value': 'a'})


def test_allows_nullable_inputs_to_be_set_to_a_value_directly():
    doc = '''
    {
        fieldWithNullableStringInput(input: "a")
    }
    '''
    check(doc, {
        'data': {
            'fieldWithNullableStringInput': '"a"'
        }
    })


def test_does_not_allow_non_nullable_inputs_to_be_omitted_in_a_variable():
    doc = '''
    query SetsNonNullable($value: String!) {
        fieldWithNonNullableStringInput(input: $value)
    }
    '''
    with raises(GraphQLError) as excinfo:
        check(doc, {})

    assert format_error(excinfo.value) == {
        'locations': [{'column': 27, 'line': 2}],
        'message': 'Variable "$value" of required type "String!" was not provided.'
    }


def test_does_not_allow_non_nullable_inputs_to_be_set_to_null_in_a_variable():
    doc = '''
    query SetsNonNullable($value: String!) {
        fieldWithNonNullableStringInput(input: $value)
    }
    '''

    with raises(GraphQLError) as excinfo:
        check(doc, {}, {'value': None})

    assert format_error(excinfo.value) == {
        'locations': [{'column': 27, 'line': 2}],
        'message': 'Variable "$value" of required type "String!" was not provided.'
    }


def test_allows_non_nullable_inputs_to_be_set_to_a_value_in_a_variable():
    doc = '''
    query SetsNonNullable($value: String!) {
        fieldWithNonNullableStringInput(input: $value)
    }
    '''

    check(doc, {
        'data': {
            'fieldWithNonNullableStringInput': '"a"'
        }
    }, {'value': 'a'})


def test_allows_non_nullable_inputs_to_be_set_to_a_value_directly():
    doc = '''
    {
        fieldWithNonNullableStringInput(input: "a")
    }
    '''

    check(doc, {
        'data': {
            'fieldWithNonNullableStringInput': '"a"'
        }
    })


def test_passes_along_null_for_non_nullable_inputs_if_explcitly_set_in_the_query():
    doc = '''
    {
        fieldWithNonNullableStringInput
    }
    '''

    check(doc, {
        'data': {
            'fieldWithNonNullableStringInput': None
        }
    })


def test_allows_lists_to_be_null():
    doc = '''
    query q($input: [String]) {
        list(input: $input)
    }
    '''

    check(doc, {
        'data': {
            'list': None
        }
    })


def test_allows_lists_to_contain_values():
    doc = '''
    query q($input: [String]) {
        list(input: $input)
    }
    '''

    check(doc, {
        'data': {
            'list': stringify(['A'])
        }
    }, {'input': ['A']})


def test_allows_lists_to_contain_null():
    doc = '''
    query q($input: [String]) {
        list(input: $input)
    }
    '''

    check(doc, {
        'data': {
            'list': stringify(['A', None, 'B'])
        }
    }, {'input': ['A', None, 'B']})


def test_does_not_allow_non_null_lists_to_be_null():
    doc = '''
    query q($input: [String]!) {
        nnList(input: $input)
    }
    '''

    with raises(GraphQLError) as excinfo:
        check(doc, {}, {'input': None})

    assert format_error(excinfo.value) == {
        'locations': [{'column': 13, 'line': 2}],
        'message': 'Variable "$input" of required type "[String]!" was not provided.'
    }


def test_allows_non_null_lists_to_contain_values():
    doc = '''
    query q($input: [String]!) {
        nnList(input: $input)
    }
    '''

    check(doc, {
        'data': {
            'nnList': stringify(['A'])
        }
    }, {'input': ['A']})


def test_allows_non_null_lists_to_contain_null():
    doc = '''
    query q($input: [String]!) {
        nnList(input: $input)
    }
    '''

    check(doc, {
        'data': {
            'nnList': stringify(['A', None, 'B'])
        }
    }, {'input': ['A', None, 'B']})


def test_allows_lists_of_non_nulls_to_be_null():
    doc = '''
    query q($input: [String!]) {
        listNN(input: $input)
    }
    '''

    check(doc, {
        'data': {
            'listNN': None
        }
    }, {'input': None})


def test_allows_lists_of_non_nulls_to_contain_values():
    doc = '''
    query q($input: [String!]) {
        listNN(input: $input)
    }
    '''

    check(doc, {
        'data': {
            'listNN': stringify(['A'])
        }
    }, {'input': ['A']})


def test_does_not_allow_lists_of_non_nulls_to_contain_null():
    doc = '''
    query q($input: [String!]) {
        listNN(input: $input)
    }
    '''

    params = {'input': ['A', None, 'B']}

    with raises(GraphQLError) as excinfo:
        check(doc, {}, params)

    assert format_error(excinfo.value) == {
        'locations': [{'column': 13, 'line': 2}],
        'message': 'Variable "$input" got invalid value {}.\n'
                   'In element #1: Expected "String!", found null.'.format(stringify(params['input']))
    }


def test_does_not_allow_non_null_lists_of_non_nulls_to_be_null():
    doc = '''
    query q($input: [String!]!) {
        nnListNN(input: $input)
    }
    '''
    with raises(GraphQLError) as excinfo:
        check(doc, {}, {'input': None})

    assert format_error(excinfo.value) == {
        'locations': [{'column': 13, 'line': 2}],
        'message': 'Variable "$input" of required type "[String!]!" was not provided.'
    }


def test_allows_non_null_lists_of_non_nulls_to_contain_values():
    doc = '''
    query q($input: [String!]!) {
        nnListNN(input: $input)
    }
    '''

    check(doc, {
        'data': {
            'nnListNN': stringify(['A'])
        }
    }, {'input': ['A']})


def test_does_not_allow_non_null_lists_of_non_nulls_to_contain_null():
    doc = '''
    query q($input: [String!]!) {
        nnListNN(input: $input)
    }
    '''

    params = {'input': ['A', None, 'B']}

    with raises(GraphQLError) as excinfo:
        check(doc, {}, params)

    assert format_error(excinfo.value) == {
        'locations': [{'column': 13, 'line': 2}],
        'message': 'Variable "$input" got invalid value {}.\n'
                   'In element #1: Expected "String!", found null.'.format(stringify(params['input']))
    }


def test_does_not_allow_invalid_types_to_be_used_as_values():
    doc = '''
    query q($input: TestType!) {
        fieldWithObjectInput(input: $input)
    }
    '''
    params = {'input': {'list': ['A', 'B']}}

    with raises(GraphQLError) as excinfo:
        check(doc, {}, params)

    assert format_error(excinfo.value) == {
        'locations': [{'column': 13, 'line': 2}],
        'message': 'Variable "$input" expected value of type "TestType!" which cannot be used as an input type.'
    }


def test_does_not_allow_unknown_types_to_be_used_as_values():
    doc = '''
    query q($input: UnknownType!) {
        fieldWithObjectInput(input: $input)
    }
    '''
    params = {'input': 'whoknows'}

    with raises(GraphQLError) as excinfo:
        check(doc, {}, params)

    assert format_error(excinfo.value) == {
        'locations': [{'column': 13, 'line': 2}],
        'message': 'Variable "$input" expected value of type "UnknownType!" which cannot be used as an input type.'
    }


# noinspection PyMethodMayBeStatic
class TestUsesArgumentDefaultValues:

    def test_when_no_argument_provided(self):
        check('{ fieldWithDefaultArgumentValue }', {
            'data': {
                'fieldWithDefaultArgumentValue': '"Hello World"'
            }
        })

    def test_when_nullable_variable_provided(self):
        check('''
        query optionalVariable($optional: String) {
            fieldWithDefaultArgumentValue(input: $optional)
        }
        ''', {
            'data': {
                'fieldWithDefaultArgumentValue': '"Hello World"'
            }
        })

    def test_when_argument_provided_cannot_be_parsed(self):
        check('''
        {
            fieldWithDefaultArgumentValue(input: WRONG_TYPE)
        }
        ''', {
            'data': {
                'fieldWithDefaultArgumentValue': '"Hello World"'
            }
        })
