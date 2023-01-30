import scio
import helpers
from lxml import etree


def transport(req):
    return helpers.support('NilDateResp.xml', 'r')


client = scio.Client(helpers.support('NilDate.wsdl', 'r'),
                     transport=transport)


def test_simple_date():
    notnil = client.type.getNilDateResponse('2013-03-05')
    assert notnil.year == 2013
    assert notnil.month == 3
    assert notnil.day == 5


def test_nil_simple_date():
    nil = client.type.getNilDateResponse()
    assert nil is None


def test_simple_datetime():
    notnil = client.type.getNilDateTimeResponse('2013-03-05T12:01:02')
    assert notnil.year == 2013
    assert notnil.month == 3
    assert notnil.day == 5
    assert notnil.hour == 12
    assert notnil.minute == 1
    assert notnil.second == 2


def test_nil_simple_datetime():
    nil = client.type.getNilDateTimeResponse()
    assert nil is None


def test_deserialize_complex_nil_response():
    resp = client.service.getNilDateAndDateTime('foo')

    # regular nils are nil
    assert resp.nilDate is None
    assert resp.nilDateTime is None

    # regular non-nils are sane
    assert resp.niceDate.year == 1955
    assert resp.niceDate.month == 11
    assert resp.niceDate.day == 5
    assert resp.niceDateTime.year == 1955
    assert resp.niceDateTime.month == 11
    assert resp.niceDateTime.day == 12
    assert resp.niceDateTime.hour == 22
    assert resp.niceDateTime.minute == 4
    assert resp.niceDateTime.second == 0

    # nils with other attrs are nil
    assert resp.niceNilDate is None
