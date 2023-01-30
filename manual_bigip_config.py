"""
this is a set of tests for the bigip_config class
unfortunately it needs to be manually run for now... 

the problem is that there is no abstraction between iCR calls
and the ansible module implementation, thus, to test the code, 
parts of the ansible module need to be commented out. Fixing this
woud require some kind of python module which wraps iCR calls, but
that seems to defeat the point of providing a Rest library in
the first place...
"""


import sys
import json
import requests
from copy import deepcopy

from requests.exceptions import ConnectionError, HTTPError, Timeout, TooManyRedirects

image_b64 = "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"

class NoChangeError(Exception):
	pass

class BigipConfig(object):
  def __init__(self, module):
    self.host = module.params["host"]
    self.user = module.params["user"]
    self.password = module.params["password"]
    self.state = module.params["state"]

    try: 
    	self.payload = json.loads(module.params.get("payload"))
    except TypeError:
    	self.payload = ''
    self.resource_id = module.params.get("resource_id")
    self.resource_key = module.params.get("resource_key")

    self.collection_path = module.params["collection_path"]
    self.hosturl = "https://%s" % self.host
    self.auth = (self.user, self.password)

  def _get_full_resource_id(self):
    if self.resource_id is not None:
      return self.resource_id
    else:
      # need to extract the id from payload
      return self.payload[self.resource_key]

  def _get_full_resource_path(self):
    # https://localhost/mgmt/tm/sys/application/service/~Common~Vip1_demo_iApp.app~Vip1_demo_iApp
    if 'application/service' in self.collection_path:
      return ('%s/~Common~%s.app~%s' % (self.collection_path,
         self._get_full_resource_id(), self._get_full_resource_id()))
    elif self.resource_selfLink:
      return self.resource_selfLink[self.resource_selfLink.find('mgmt'):]
    else:
      return '%s/%s' % (self.collection_path, self._get_full_resource_id())

  def inspect(self):
    return self.http("get", self.collection_path)

  def _get_safe_patch_payload(self):
    """
      When using the HTTP patch method, there are certain
      field which may not be present in the payload 
    """
    safe_payload = deepcopy(self.payload)
    
    #  => {"code":400,"message":"\"network\" may not be specified in the context of the \"modify\" command.
    #   \"network\" may be specified using the following commands: create, list, show","errorStack":[]}
    if safe_payload.get("network", None) is not None:
      del safe_payload["network"]

    # => {"code":400,"message":"\"type\" may not be specified in the context of the \"modify\" command.
    #    \"type\" may be specified using the following commands: create, edit, list","errorStack":[]}
    if safe_payload.get("type", None) is not None:
      del safe_payload["type"]

    del safe_payload[self.resource_key]
    if len(safe_payload) < 1:
      raise NoChangeError('Payload is empty')

    # handle the application service resources (i.e. iApps)
    # if 'application/service' in self.collection_path:
    #   print 'collection_path = {}'.format(self.collection_path)

    return safe_payload

  def resource_exists(self):
    #for collections that we want to patch (for example sys/global-settings)
    # there is no resource_key which we can use to determine existance
    if self.resource_key is None:
      return False

    exists = False
    (rc, out, err) = self.http("get", self.collection_path)

    if rc != 0:
      raise ValueError("Bad return code from HTTP GET. %s " % err)

    items = out.get("items", None)
    if items is not None:
      for i in items:
        if i[self.resource_key] == self.payload[self.resource_key]:
          exists = True
          self.set_selfLink(i)
          print 'fullPath = {}'.format(i['fullPath'])
          break
    return exists

  def set_selfLink(self, config_item):
    # self link looks like https://localhost/mgmt/tm/asm/policies/vsyrM5HMMpOHlSwDfs8mLA"
    self.resource_selfLink = config_item['selfLink']

  def create_or_update_resource(self):
    # if it is a collection, we can just patch 
    if self.resource_key is None:
      return self.http("patch", self.collection_path, self.payload)
    elif "mgmt/tm/asm/tasks/" in self.collection_path:
      return self.create_resource()
    else:
      if self.resource_exists():
        try: 
          return self.update_resource()
        except NoChangeError, e:
          rc = 0
          out = 'No configuration changes necessary. {}'.format(e)
          err = ''
          return (rc, out, err)
      else:
        return self.create_resource()

  def create_resource(self):
    return self.http("post", self.collection_path, self.payload)

  def update_resource(self):
      return self.http("patch", self._get_full_resource_path(),
        self._get_safe_patch_payload())

  def delete_resource(self):
    return self.http("delete", self._get_full_resource_path())

  def http(self, method, host, payload=''):
    print 'HTTP %s %s: %s' % (method, host, payload)
    methodfn = getattr(requests, method.lower(), None)
    if method is None:
      raise NotImplementedError("requests module has not method %s " % method)
    try:
      if payload != '':
        request = methodfn(url='%s/%s' % (self.hosturl, host), data=json.dumps(payload), auth=self.auth, verify=False)
      else:
        request = methodfn(url='%s/%s' % (self.hosturl, host), auth=self.auth, verify=False)

      if request.status_code != requests.codes.ok:
        request.raise_for_status()

      rc = 0
      out = json.loads(request.text)
      err = ''
    except (ConnectionError, HTTPError, Timeout, TooManyRedirects) as e:
      rc = 1
      out = ''
      err = '%s. Error received: %s.\n Sent request: %s' % (
          e.message, json.loads(request.text), 'HTTP %s %s: %s' % (method, host, payload))

    print 'HTTP %s returned: %s' % (method, request.text)

    return (rc, out, err)

def get_namespace(**kwargs):
  class Namespace(object):
    def __init__(self, kwargs):
      for k, v in kwargs.items():
        setattr(self, k, v)
  return Namespace(kwargs)

# uncomment the below and run as necessary as 
# bash$ python ./manual_bigip_config.py

hostname="52.0.182.115"
user="rest_admin"
password="GoF5!"

# test problems with data-group patch, specifically
#   does not like the 'type' field
# module = get_namespace()
# module.params = {
#   "host": hostname,
#   "user": user,
#   "password": password,
#   "state": "present",
#   "payload": '{"name":"sorry_images", "type":"string", "records":[{"name":"'+image_b64+'"}]}',
#   "collection_path": "mgmt/tm/ltm/data-group/internal",
#   "resource_key": "name",
#   "resource_id": None  
# }

# test problems uploading analytics profile, specifically
#   does not like the 'type' field
# module = get_namespace()
# module.params = {
#   "host": hostname,
#   "user": user,
#   "password": password,
#   "state": "present",
#   "payload": '{"name":"demo_analytics_profile","capturedTrafficExternalLogging":"disabled","capturedTrafficInternalLogging":"disabled","collectGeo":"enabled","collectIp":"enabled","collectMaxTpsAndThroughput":"enabled","collectMethods":"enabled","collectPageLoadTime":"enabled","collectResponseCodes":"enabled","collectSubnets":"enabled","collectUrl":"enabled","collectUserAgent":"enabled","collectUserSessions":"enabled","collectedStatsExternalLogging":"disabled","collectedStatsInternalLogging":"enabled","defaultsFrom":"/Common/analytics","notificationByEmail":"disabled","notificationBySnmp":"disabled","notificationBySyslog":"disabled","partition":"Common","publishIruleStatistics":"disabled","sampling":"enabled","sessionCookieSecurity":"ssl-only","sessionTimeoutMinutes":"5"}',
#   "collection_path": "mgmt/tm/ltm/profile/analytics",
#   "resource_key": "name",
#   "resource_id": None  
# }

iapp_payload = {
    "name": "Vip1_demo_iApp",
    "inheritedDevicegroup": "true",
    "inheritedTrafficGroup": "true",
    "lists": [
        {
            "encrypted": "no",
            "name": "irules__irules",
            "value": [
                "/Common/__demo_analytics_rule",
                "/Common/__sorry_page_rule"
            ]
        }
    ],
    "partition": "Common",
    "strictUpdates": "enabled",
    "tables": [
        {
            "name": "basic__snatpool_members"
        },
        {
            "name": "net__snatpool_members"
        },
        {
            "name": "optimizations__hosts"
        },
        {
            "columnNames": [
                "name"
            ],
            "name": "pool__hosts",
            "rows": [
                {
                    "row": [
                        "demo.example.com"
                    ]
                }
            ]
        },
        {
            "name": "pool__members"
        },
        {
            "name": "server_pools__servers"
        }
    ],
    "template": "/Common/f5.http",
    "templateModified": "no",
    "trafficGroup": "/Common/traffic-group-1",
    "variables": [
        {
            "encrypted": "no",
            "name": "client__http_compression",
            "value": "/Common/wan-optimized-compression"
        },
        {
            "encrypted": "no",
            "name": "client__standard_caching_without_wa",
            "value": "/#do_not_use#"
        },
        {
            "encrypted": "no",
            "name": "client__tcp_wan_opt",
            "value": "/Common/tcp-ssl-wan-optimized"
        },
        {
            "encrypted": "no",
            "name": "net__client_mode",
            "value": "wan"
        },
        {
            "encrypted": "no",
            "name": "net__route_to_bigip",
            "value": "no"
        },
        {
            "encrypted": "no",
            "name": "net__same_subnet",
            "value": "no"
        },
        {
            "encrypted": "no",
            "name": "net__server_mode",
            "value": "lan"
        },
        {
            "encrypted": "no",
            "name": "net__snat_type",
            "value": "automap"
        },
        {
            "encrypted": "no",
            "name": "net__vlan_mode",
            "value": "all"
        },
        {
            "encrypted": "no",
            "name": "pool__addr",
            "value": "172.16.23.106"
        },
        {
            "encrypted": "no",
            "name": "pool__http",
            "value": "/#create_new#"
        },
        {
            "encrypted": "no",
            "name": "pool__mask",
            "value": ""
        },
        {
            "encrypted": "no",
            "name": "pool__mirror",
            "value": "disabled"
        },
        {
            "encrypted": "no",
            "name": "pool__persist",
            "value": "/#do_not_use#"
        },
        {
            "encrypted": "no",
            "name": "pool__pool_to_use",
            "value": "/Common/Vip1_pool"
        },
        {
            "encrypted": "no",
            "name": "pool__port",
            "value": "80"
        },
        {
            "encrypted": "no",
            "name": "server__ntlm",
            "value": "/#do_not_use#"
        },
        {
            "encrypted": "no",
            "name": "server__oneconnect",
            "value": "/#do_not_use#"
        },
        {
            "encrypted": "no",
            "name": "server__tcp_lan_opt",
            "value": "/Common/tcp-ssl-wan-optimized"
        },
        {
            "encrypted": "no",
            "name": "server__tcp_req_queueing",
            "value": "no"
        },
        {
            "encrypted": "no",
            "name": "pool__port_secure",
            "value": "443"
        },
        {
            "encrypted": "no",
            "name": "pool__redirect_port",
            "value": "80"
        },
        {
            "encrypted": "no",
            "name": "pool__redirect_to_https",
            "value": "yes"
        },
        {
            "encrypted": "no",
            "name": "pool__xff",
            "value": "yes"
        },
        {
            "encrypted": "no",
            "name": "ssl__mode",
            "value": "client_ssl"
        },
        {
            "encrypted": "no",
            "name": "ssl__cert",
            "value": "/Common/default.crt"
        },
        {
            "encrypted": "no",
            "name": "ssl__client_ssl_profile",
            "value": "/#create_new#"
        },
        {
            "encrypted": "no",
            "name": "ssl__key",
            "value": "/Common/default.key"
        },
        {
            "encrypted": "no",
            "name": "ssl__use_chain_cert",
            "value": "/#do_not_use#"
        },
        {
            "encrypted": "no",
            "name": "ssl_encryption_questions__advanced",
            "value": "yes"
        },
        {
            "encrypted": "no",
            "name": "ssl_encryption_questions__help",
            "value": "hide"
        },
        {
            "encrypted": "no",
            "name": "stats__analytics",
            "value": "/Common/demo_analytics_profile"
        },
        {
            "encrypted": "no",
            "name": "stats__request_logging",
            "value": "/Common/request-log"
        }
    ]
}

# # test problems uploading iApps (something to do with .app in the name)
# module = get_namespace()
# module.params = {
#   "host": hostname,
#   "user": user,
#   "password": password,
#   "state": "present",
#   "payload": json.dumps(iapp_payload),
#   "collection_path": "mgmt/tm/sys/application/service",
#   "resource_key": "name",
#   "resource_id": None  
# }


# module = get_namespace()
# module.params = {
#   "host": hostname,
#   "user": user,
#   "password": password,
#   "state": "present",
#   "payload": '{"name": "setup.run", "value":"false"}',
#   "collection_path": "mgmt/tm/sys/db",
#   "resource_key": "name",
#   "resource_id": None  
# } 

# module = get_namespace()
# module.params = {
#   "host": hostname,
#   "user": user,
#   "password": password,
#   "state": "present",
#   "payload": '{"name":"us-east-1"}',
#   "collection_path": "mgmt/tm/gtm/datacenter",
#   "resource_key": "name",
#   "resource_id": None
# } 

# with open('/aws-deployments/roles/bigip_app1/files/asm_policy_linux_high_base64', 'r') as f:
# 	asm_policy_linux_high_base64 = f.read()[0:-1]

# print asm_policy_linux_high_base64[0:10]

# module = get_namespace()
# module.params = {
#   "host": hostname,
#   "user": user,
#   "password": password,
#   "state": "present",
#   "payload": r'{"file":"'+asm_policy_linux_high_base64+'","isBase64":true,"policyReference":{"link":"https://localhost/mgmt/tm/asm/policies/v2VUm_ocG5oFz7CSGWq-xw" } }',
#   "collection_path": "mgmt/tm/asm/tasks/import-policy",
#   "resource_key": "name",
# } 

module = get_namespace()
module.params = {
  "host": hostname,
  "user": user,
  "password": password,
  "state": "inspect",
  "collection_path": "mgmt/tm/asm/tasks/import-policy/elICMlpQ3bLiT1ocb3Ckgg"
} 

print BigipConfig(module).inspect()



#bigip_config = BigipConfig(module).create_or_update_resource()
