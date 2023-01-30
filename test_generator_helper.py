# encoding: utf-8
from collections import OrderedDict
from zerotest.request import Request
from zerotest.utils.generator_helper import (
    get_name_from_request,
    dict_to_param_style_code
)


#: Common HTTP request path characters that are invalid when used for
#: a python function name.
INVALID_CHARS = (
    '*',
    '-',
    '#',
    '/',
    '.'
)


def test_get_name_from_request():
    req = Request(path='/', method='GET')
    assert get_name_from_request(req) == 'get_root'
    req = Request(path='/the/world', method='PUT')
    assert get_name_from_request(req) == 'put_the_world'

    for invalid_char in INVALID_CHARS:
        assert(
            get_name_from_request(
                Request(
                    path='/bad_{0}_trailing'.format(invalid_char),
                    method='GET'
                )
            ) == 'get_bad_trailing'
        )


def test_dict_to_param_style_code():
    test_dict = OrderedDict()
    test_dict['param_a'] = 'A'
    test_dict['test_c'] = 'C'
    assert dict_to_param_style_code(test_dict) == "param_a='A', test_c='C'"
