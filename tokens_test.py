# -*- coding: utf-8 -*-

import datetime

import mock
from pyramid.testing import DummyRequest
import pytest

from h import db
from h.auth import models
from h.auth import tokens


def test_generate_jwt_calls_encode(jwt):
    """It should pass the right arguments to encode()."""
    before = datetime.datetime.utcnow()
    request = mock_request()

    tokens.generate_jwt(request, 3600)

    assert jwt.encode.call_args[0][0]['sub'] == 'acct:testuser@hypothes.is', (
        "It should encode the userid as 'sub'")
    after = datetime.datetime.utcnow() + datetime.timedelta(seconds=3600)
    assert before < jwt.encode.call_args[0][0]['exp'] < after, (
        "It should encode the expiration time as 'exp'")
    assert jwt.encode.call_args[0][0]['aud'] == request.host_url, (
        "It should encode request.host_url as 'aud'")
    assert jwt.encode.call_args[1]['algorithm'] == 'HS256', (
        "It should pass the right algorithm to encode()")


def test_generate_jwt_when_authenticated_userid_is_None(jwt):
    """It should work when request.authenticated_userid is None."""
    request = mock_request()
    request.authenticated_userid = None

    tokens.generate_jwt(request, 3600)

    assert jwt.encode.call_args[0][0]['sub'] is None


def test_generate_jwt_returns_token(jwt):
    assert (tokens.generate_jwt(mock_request(), 3600) ==
            jwt.encode.return_value)


def test_userid_from_jwt_calls_decode(jwt):
    request = mock_request()
    tokens.userid_from_jwt(u'abc123', request)

    assert jwt.decode.call_args[0] == (u'abc123',), (
        "It should pass the correct token to decode()")
    assert (jwt.decode.call_args[1]['key'] ==
            request.registry.settings['h.client_secret']), (
        "It should pass the right secret key to decode()")
    assert jwt.decode.call_args[1]['audience'] == request.host_url, (
        "It should pass the right audience to decode()")
    assert jwt.decode.call_args[1]['leeway'] == 240, (
        "It should pass the right leeway to decode()")
    assert jwt.decode.call_args[1]['algorithms'] == ['HS256'], (
        "It should pass the right algorithms to decode()")


def test_userid_from_jwt_returns_sub_from_decode(jwt):
    jwt.decode.return_value = {'sub': 'acct:test_user@hypothes.is'}

    result = tokens.userid_from_jwt(u'abc123', mock_request())

    assert result == 'acct:test_user@hypothes.is'


def test_userid_from_jwt_returns_None_if_no_sub(jwt):
    jwt.decode.return_value = {}  # No 'sub' key.

    result = tokens.userid_from_jwt(u'abc123', mock_request())

    assert result is None


def test_userid_from_jwt_returns_None_if_decoding_fails(jwt):
    class InvalidTokenError(Exception):
        pass
    jwt.InvalidTokenError = InvalidTokenError
    jwt.decode.side_effect = InvalidTokenError

    result = tokens.userid_from_jwt(u'abc123', mock_request())

    assert result is None


def test_generate_jwt_userid_from_jwt_successful():
    """Test generate_jwt() and userid_from_jwt() together.

    Test that userid_from_jwt() successfully decodes tokens
    generated by generate_jwt().

    """
    token = tokens.generate_jwt(mock_request(), 3600)
    userid = tokens.userid_from_jwt(token, mock_request())

    assert userid == 'acct:testuser@hypothes.is'


def test_generate_jwt_userid_from_jwt_bad_token():
    """Test generate_jwt() and userid_from_jwt() together.

    Test that userid_from_jwt() correctly fails to decode a token
    generated by generate_jwt() using the wrong secret.

    """
    request = mock_request()
    request.registry.settings['h.client_secret'] = 'wrong'
    token = tokens.generate_jwt(request, 3600)

    userid = tokens.userid_from_jwt(token, mock_request())

    assert userid is None


def test_userid_from_api_token_returns_None_when_token_doesnt_start_with_prefix():
    """
    As a sanity check, don't even attempt to look up tokens that don't start
    with the expected prefix.
    """
    token = models.Token('acct:foo@example.com')
    token.value = u'abc123'
    db.Session.add(token)

    result = tokens.userid_from_api_token(u'abc123')

    assert result is None


def test_userid_from_api_token_returns_None_for_nonexistent_tokens():
    madeuptoken = models.Token.prefix + '123abc'

    result = tokens.userid_from_api_token(madeuptoken)

    assert result is None


def test_userid_from_api_token_returns_userid_for_valid_tokens():
    token = models.Token('acct:foo@example.com')
    db.Session.add(token)

    result = tokens.userid_from_api_token(token.value)

    assert result == 'acct:foo@example.com'


def test_authenticated_userid_is_none_if_header_missing():
    request = DummyRequest()

    assert tokens.authenticated_userid(request) is None


@pytest.mark.parametrize('value', [
    'junk header',
    'bearer:wibble',
    'Bearer',
    'Bearer ',
])
def test_authenticated_userid_is_none_if_header_incorrectly_formatted(value):
    request = DummyRequest(headers={'Authorization': value})

    assert tokens.authenticated_userid(request) is None


@mock.patch('h.auth.tokens.userid_from_api_token')
@mock.patch('h.auth.tokens.userid_from_jwt')
def test_authenticated_userid_passes_token_to_extractor_functions(jwt, api_token):
    api_token.return_value = None
    jwt.return_value = None
    request = DummyRequest(headers={'Authorization': 'Bearer f00ba12'})

    tokens.authenticated_userid(request)

    api_token.assert_called_once_with('f00ba12')
    jwt.assert_called_once_with('f00ba12', request)


@mock.patch('h.auth.tokens.userid_from_api_token')
@mock.patch('h.auth.tokens.userid_from_jwt')
def test_authenticated_userid_returns_userid_from_api_token_if_present(jwt, api_token):
    api_token.return_value = 'acct:foo@example.com'
    jwt.return_value = 'acct:bar@example.com'
    request = DummyRequest(headers={'Authorization': 'Bearer f00ba12'})

    result = tokens.authenticated_userid(request)

    assert result == 'acct:foo@example.com'


@mock.patch('h.auth.tokens.userid_from_api_token')
@mock.patch('h.auth.tokens.userid_from_jwt')
def test_authenticated_userid_returns_userid_from_jwt_as_fallback(jwt, api_token):
    api_token.return_value = None
    jwt.return_value = 'acct:bar@example.com'
    request = DummyRequest(headers={'Authorization': 'Bearer f00ba12'})

    result = tokens.authenticated_userid(request)

    assert result == 'acct:bar@example.com'


@mock.patch('h.auth.tokens.userid_from_api_token')
@mock.patch('h.auth.tokens.userid_from_jwt')
def test_authenticated_userid_returns_none_if_neither_token_valid(jwt, api_token):
    api_token.return_value = None
    jwt.return_value = None
    request = DummyRequest(headers={'Authorization': 'Bearer f00ba12'})

    result = tokens.authenticated_userid(request)

    assert result is None


def mock_request(token=None):
    request = mock.Mock(authenticated_userid='acct:testuser@hypothes.is',
                        host_url='https://hypothes.is')
    request.registry.settings = {
        'h.client_id': 'id',
        'h.client_secret': 'secret'
    }
    if token:
        request.headers = {'Authorization': token}
    return request


@pytest.fixture
def jwt(patch):
    return patch('h.auth.tokens.jwt')
