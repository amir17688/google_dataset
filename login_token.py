# wwwhisper - web access control.
# Copyright (C) 2016 Jan Wrobel <jan@mixedbit.org>

import datetime

from django.conf import settings
from django.core import signing

"""Returns float that has microseconds resolution"""
def _datetime_to_timestamp(datetime_arg):
    # It does not matter what timezone and start time is used here.
    # It is only important that the output of this function increases
    # when datetime_arg increases.
    return (datetime_arg - datetime.datetime(2015,1,1)).total_seconds()

def generate_login_token(site, site_url, email):
    """Returns a signed token to login a user with a given email.

    The token should be emailed to the user to verify that the user
    indeed owns the email.

    The token is valid only for the current site (it will be discarded
    if it is submitted to a different site protected by the same
    wwwhisper instance).

    The token allows only for one succesful login.
    """
    timestamp = 0
    user = site.users.find_item_by_email(email)
    if user is not None and user.last_login is not None:
        # Successul login changes user.last_login, which invalidates
        # all tokens generated for the user.
        timestamp = _datetime_to_timestamp(user.last_login)
    token_data = {
        'site': site_url,
        'email': email,
        'timestamp': timestamp
    }
    return signing.dumps(token_data, salt=site_url, compress=True)

def load_login_token(site, site_url, token):
    """Verifies the login token.

    Returns email encoded in the token if the token is valid, None
    otherwise.
    """
    try:
        token_data = signing.loads(
            token, salt=site_url, max_age=settings.AUTH_TOKEN_SECONDS_VALID)
        # site_url in the token seems like an overkill. site_url is
        # already used as salt which should give adequate protection
        # against using a token for sites different than the one for
        # which the token was generated.
        if token_data['site'] != site_url:
            return None
        email = token_data['email']
        timestamp = token_data['timestamp']
        user = site.users.find_item_by_email(email)
        if user is not None and user.last_login is not None:
            if _datetime_to_timestamp(user.last_login) != timestamp:
                return None
        elif timestamp != 0:
            return None
        return email
    except signing.BadSignature:
        return None
