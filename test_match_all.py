# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyeqs.dsl import MatchAll
from tests.helpers import homogeneous


def test_add_match_all():
    """
    Create Match All Block
    """
    # When add a match all filter
    t = MatchAll()

    # Then I see the appropriate JSON
    results = {
        "match_all": {}
    }

    homogeneous(t, results)
   t = QuerySet("localhost", index="foo")

    # And there are records
    add_document("foo", {"bar": "baz", "foo": "foo"})
    add_document("foo", {"bar": "bazbaz", "foo": "foo"})
    add_document("foo", {"bar": "baz", "foo": "foofoo"})
    add_document("foo", {"bar": "baz", "foo": "foofoofoo"})

    # And I filter match_all
    t.filter(MatchAll())
    results = t[0:10]

    # Then I get a the expected results
    len(results).should.equal(4)
