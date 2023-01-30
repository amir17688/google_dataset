from zerotest.forwarder import Forwarder


request = None
response = None


def test_callback():
    def callback(req, res):
        global request
        global response
        request = req
        response = res

    forwarder = Forwarder('http://example.com')
    forwarder.on_forward_complete(callback)
    fake_request = object()
    fake_response = object()
    forwarder.trigger_on_forward_complete(fake_request, fake_response)
    assert request == fake_request
    assert response == fake_response
