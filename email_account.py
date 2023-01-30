from contextio.lib.resources.base_resource import BaseResource
from contextio.lib.resources.connect_token import ConnectToken
from contextio.lib.resources.folder import Folder

class EmailAccount(BaseResource):
    resource_id = "label"
    keys = [
        "status", "resource_url", "type", "authentication_type", "use_ssl", "server", "label",
        "username", "port"
    ]

    def __init__(self, parent, definition):
        super(EmailAccount, self).__init__(parent, 'email_accounts/{label}', definition)

    def post(self, **kwargs):
        all_args = ["delimiter"]

        for prop in all_args:
            value = kwargs.get(prop)
            if value:
                setattr(self, prop, value)

        return super(EmailAccount, self).post(params=kwargs, all_args=all_args)

    def get_folders(self):
        return [Folder(self, obj) for obj in self._request_uri("folders")]

    def get_connect_tokens(self):
        return [ConnectToken(self, obj) for obj in self._request_uri("connect_tokens")]
