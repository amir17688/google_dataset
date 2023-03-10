
"""
Copyright (c) 2016, Guy Bowerman
Description: Simple Azure Resource Manager Python library
License: MIT (see LICENSE.txt file for details)
"""

# subnfs - place to store azurerm functions related to subscriptions

from .settings import azure_rm_endpoint, BASE_API
from .restfns import do_get

# list_locations(access_token, subscrpition_id)
# list available locations for a subscription
def list_locations(access_token, subscription_id):
    endpoint = ''.join([azure_rm_endpoint, 
	                    '/subscriptions/', subscription_id,
			            '/locations?api-version=', BASE_API]) 
    return do_get(endpoint, access_token)

# list_subscriptions(access_token)
# list the available Azure subscriptions for this user/service principle
def list_subscriptions(access_token):
    endpoint = ''.join([azure_rm_endpoint, 
	                    '/subscriptions/', 
			            '?api-version=', BASE_API]) 
    return do_get(endpoint, access_token)
