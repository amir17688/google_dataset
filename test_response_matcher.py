import json

import pytest

from zerotest.fuzzy_matcher import FuzzyMatchWarning
from zerotest.response import Response
from zerotest.response_matcher import ResponseMatcher


def test_compare():
    matcher = ResponseMatcher()
    r1 = Response(status=200, headers={"a": "1"}, body="ok")
    r2 = Response(status=200, headers={"a": "1"}, body="ok")
    matcher.match_responses(r1, r2)
    r2.body = "not ok"
    with pytest.raises(AssertionError):
        matcher.match_responses(r1, r2)
    r2.body = "ok"
    r2.status = 201
    with pytest.raises(AssertionError):
        matcher.match_responses(r1, r2)
    r2.status = 200
    r2.headers['b'] = 2
    with pytest.raises(AssertionError):
        matcher.match_responses(r1, r2)
    del r2.headers['b']
    matcher.match_responses(r1, r2)


def test_ignore_headers_compare():
    matcher = ResponseMatcher(ignore_headers=['c', 'd', 'e'])
    r1 = Response(status=200, headers={"a": "1", "c": "not"}, body="ok")
    r2 = Response(status=200, headers={"a": "1", "c": "same"}, body="ok")
    matcher.match_responses(r1, r2)
    r1.headers['d'] = "ignored should"
    matcher.match_responses(r1, r2)
    r2.headers['e'] = "ignored should"
    matcher.match_responses(r1, r2)
    r1.headers['g'] = "not ignored"
    with pytest.raises(AssertionError):
        matcher.match_responses(r1, r2)


def test_ignore_all_headers_compare():
    matcher = ResponseMatcher(ignore_all_headers=True)
    r1 = Response(status=200, headers={"a": "1", "c": "not"}, body="ok")
    r2 = Response(status=200, headers={"a": "1", "c": "same", "d": 3}, body="ok")
    matcher.match_responses(r1, r2)


def test_ignore_fields_compare():
    matcher = ResponseMatcher(ignore_fields=['some_record.created_at', 'id'])
    r1 = Response(status=200, headers={}, body=json.dumps({"id": 1, "name": "test"}))
    r2 = Response(status=200, headers={}, body=json.dumps({"id": 2, "name": "test"}))
    # not work if not content-type
    with pytest.raises(AssertionError):
        matcher.match_responses(r1, r2)
    r1.headers['content-type'] = 'application/json'
    r2.headers['CONTENT-TYPE'] = 'application/json'
    matcher.match_responses(r1, r2)

    r1.body = json.dumps({"some_record.created_at": 'now', 'record': {'created_at': '111'}})
    r2.body = json.dumps({"record": {'created_at': '111'}})
    matcher.match_responses(r1, r2)

    r1.body = json.dumps({"some_record.created_at": 'now', 'some_record': {'created_at': '111'}})
    r2.body = json.dumps({"some_record": {'created_at': '111'}})
    with pytest.raises(AssertionError):
        matcher.match_responses(r1, r2)

    r1.body = json.dumps({"some_record.created_at": 'now'})
    r2.body = json.dumps({"some_record": {'created_at': '112'}})
    with pytest.raises(AssertionError):
        matcher.match_responses(r1, r2)

    # test key path under list
    r1.body = json.dumps({"some_record": [{'created_at': '1123', 'id': '0'}]})
    r2.body = json.dumps({"some_record": [{'created_at': '112', 'id': '1'}]})
    with pytest.raises(AssertionError):
        matcher.match_responses(r1, r2)

    r1.body = json.dumps({"some_record": [{'created_at': '1123', 'id': '0'}, {'created_at': '3322'}]})
    r2.body = json.dumps({"some_record": [{'created_at': '112', 'id': '1'}, {'created_at': 'tomorrow'}]})
    with pytest.raises(AssertionError):
        matcher.match_responses(r1, r2)

    r1.body = json.dumps({"some_record": [{'created_at': '1123', 'id': '1'}, {'created_at': '3322'}]})
    r2.body = json.dumps({"some_record": [{'created_at': '112', 'id': '1'}, {'created_at': 'tomorrow'}]})
    matcher.match_responses(r1, r2)


def test_fuzzy_compare():
    matcher = ResponseMatcher(fuzzy_match=True)
    allow_none_matcher = ResponseMatcher(fuzzy_match=True, fuzzy_match_options={"allow_none": True})
    allow_blank_matcher = ResponseMatcher(fuzzy_match=True, fuzzy_match_options={"allow_blank": True})
    r1 = Response(status=200, headers={}, body=json.dumps({"id": 1, "name": "test"}))
    r2 = Response(status=200, headers={}, body=json.dumps({"id": 2, "name": "test", "some_field": 0}))
    # not work if not content-type
    with pytest.raises(AssertionError):
        matcher.match_responses(r1, r2)

    r2.body = json.dumps({"id": 1, "name": "test"})
    r1.headers['content-type'] = 'application/json'
    r2.headers['CONTENT-TYPE'] = 'application/json'
    matcher.match_responses(r1, r2)

    r2.body = json.dumps({"id": "42", "name": "test42"})
    with pytest.raises(AssertionError):
        matcher.match_responses(r1, r2)

    r2.body = json.dumps({"id": 42, "name": 42})
    with pytest.raises(AssertionError):
        matcher.match_responses(r1, r2)

    r2.body = json.dumps({"id": "42", "name": 42})
    with pytest.raises(AssertionError):
        matcher.match_responses(r1, r2)

    r2.body = json.dumps({"id": 42, "name": "test42"})
    matcher.match_responses(r1, r2)

    r2.headers['use-less-header'] = True
    with pytest.raises(AssertionError):
        matcher.match_responses(r1, r2)

    r2.headers.pop('use-less-header')
    r1.body = json.dumps({"id": 1, "name": "test", "followers": []})
    r2.body = json.dumps({"id": 42, "name": "test42", "followers": [1, 2, 3]})
    matcher.match_responses(r1, r2)

    r1.body = json.dumps({"id": 1, "name": "test", "followers": ["1", "2"]})
    r2.body = json.dumps({"id": 42, "name": "test42", "followers": [1, 2, 3]})
    with pytest.raises(AssertionError):
        matcher.match_responses(r1, r2)

    r1.body = json.dumps({"id": 1, "name": "test", "followers": [1, 2]})
    matcher.match_responses(r1, r2)

    r1.body = json.dumps(
        {
            "id": 1, "name": "test", "children":
            [{"id": 2, "name": "test2"}, {"id": 3, "name": "test3"}],
            "parent": {"id": 0, "name": "test0"}
        })
    r2.body = json.dumps(
        {
            "id": 42, "name": "test", "children":
            [{"id": 4, "name": "test4"}],
            "parent": {"id": 5, "name": "test5"}
        })
    matcher.match_responses(r1, r2)

    r2.body = json.dumps(
        {
            "id": 42, "name": "test", "children":
            [{"id": 4, "name": "test4"}, {"id": "what?"}],
            "parent": {"id": 5, "name": "test5"}
        })
    with pytest.raises(AssertionError):
        matcher.match_responses(r1, r2)

    r2.body = json.dumps(
        {
            "id": 42, "name": "test", "children":
            [{"id": 4, "name": "test4"}, {}],
            "parent": {"id": "5", "name": "test5"}
        })
    with pytest.raises(AssertionError):
        matcher.match_responses(r1, r2)

    r2.body = json.dumps(
        {
            "id": 42, "name": "test", "children":
            [{"id": 4, "name": "test4"}, {}],
            "parent": {"id": "5", "name": "test5"}
        })
    with pytest.raises(AssertionError):
        matcher.match_responses(r1, r2)

    r2.body = json.dumps(
        {
            "id": 42, "name": "test", "children":
            [{"id": 4, "name": "test4"}],
            "parent": {}
        })
    with pytest.raises(AssertionError):
        matcher.match_responses(r1, r2)
    with pytest.warns(FuzzyMatchWarning):
        allow_blank_matcher.match_responses(r1, r2)

    r2.body = json.dumps(
        {
            "id": 42, "name": "test", "children":
            [{"id": 4, "name": "test4"}],
            "parent": None
        })
    with pytest.raises(AssertionError):
        matcher.match_responses(r1, r2)
    with pytest.raises(AssertionError):
        allow_blank_matcher.match_responses(r1, r2)
    with pytest.warns(FuzzyMatchWarning):
        allow_none_matcher.match_responses(r1, r2)

    r2.body = json.dumps(
        {
            "id": 42, "name": "test", "children":
            [],
            "parent": {"id": 5, "name": "test5"}
        })
    matcher.match_responses(r1, r2)
