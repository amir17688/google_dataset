###
# Copyright 2016 Hewlett Packard Enterprise, Inc. All rights reserved.
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#  http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
###

# -*- coding: utf-8 -*-
"""Helper module for working with ProLiant REST technology."""

#---------Imports---------

import os
import sys
import ssl
import time
import gzip
import json
import base64
import urllib
import ctypes
import hashlib
import logging
import httplib
import platform

from StringIO import StringIO
from collections import (OrderedDict)

import urlparse2 #pylint warning disable
from ilorest.hpilo.risblobstore2 import (BlobStore2)

#---------End of imports---------


#---------Debug logger---------

LOGGER = logging.getLogger(__name__)

#---------End of debug logger---------

class RetriesExhaustedError(Exception):
    """Raised when retry attempts have been exhausted."""
    pass

class InvalidCredentialsError(Exception):
    """Raised when invalid credentials have been provided."""
    pass

class ServerDownOrUnreachableError(Exception):
    """Raised when server is unreachable."""
    pass

class ChifDriverMissingOrNotFound(Exception):
    """Raised when chif driver is missing or not found."""
    pass

class DecompressResponseError(Exception):
    """Raised when decompressing response failed."""
    pass

class RisObject(dict):
    """Converts a json/Rest dict into a object so you can use .property
    notation"""
    __getattr__ = dict.__getitem__

    def __init__(self, d):
        super(RisObject, self).__init__()
        self.update(**dict((k, self.parse(value))
                           for k, value in d.iteritems()))

    @classmethod
    def parse(cls, value):
        """Parse for ris value"""
        if isinstance(value, dict):
            return cls(value)
        elif isinstance(value, list):
            return [cls.parse(i) for i in value]
        else:
            return value

class RestRequest(object):
    """Holder for Request information"""
    def __init__(self, path, method='GET', body=''):
        self._path = path
        self._body = body
        self._method = method

    def _get_path(self):
        """Return object path"""
        return self._path

    path = property(_get_path, None)

    def _get_method(self):
        """Return object method"""
        return self._method

    method = property(_get_method, None)

    def _get_body(self):
        """Return object body"""
        return self._body

    body = property(_get_body, None)

    def __str__(self):
        """Format string"""
        strvars = dict(
            body=self.body,
            method=self.method,
            path=self.path
        )

        # set None to '' for strings
        if not strvars['body']:
            strvars['body'] = ''

        try:
            strvars['body'] = str(str(self._body))
        except BaseException:
            strvars['body'] = ''

        return u"%(method)s %(path)s\n\n%(body)s" % strvars

class RestResponse(object):
    """Returned by Rest requests"""
    def __init__(self, rest_request, http_response):
        self._read = None
        self._status = None
        self._session_key = None
        self._session_location = None
        self._rest_request = rest_request
        self._http_response = http_response
        if self._http_response:
            self._read = self._http_response.read()
        else:
            self._read = None

    @property
    def read(self):
        """Wrapper around httpresponse.read()"""
        return self._read

    @read.setter
    def read(self, read):
        """Property for setting _read

        :param read: The data to set to read.
        :type read: str.

        """
        if read is not None:
            if isinstance(read, dict):
                read = json.dumps(read, indent=4)
            self._read = read

    def getheaders(self):
        """Property for accessing the headers"""
        return self._http_response.getheaders()

    def getheader(self, name):
        """Property for accessing an individual header

        :param name: The header name to retrieve.
        :type name: str.

        """
        return self._http_response.getheader(name, None)

    def json(self, newdict):
        """Property for setting json data

        :param newdict: The string data to set as json data.
        :type newdict: str.

        """
        self._read = json.dumps(newdict, indent=4)

    @property
    def text(self):
        """Property for accessing the data as an unparsed string"""
        return self.read

    @text.setter
    def text(self, value):
        """Property for setting text unparseddata

        :param value: The unparsed data to set as text.
        :type value: str.

        """
        self.read = value

    @property
    def dict(self):
        """Property for accessing the data as an dict"""
        return json.loads(self.text.decode('utf-8', 'ignore'))

    @property
    def obj(self):
        """Property for accessing the data as an object"""
        return RisObject.parse(self.dict)

    @property
    def status(self):
        """Property for accessing the status code"""
        if self._status:
            return self._status

        return self._http_response.status

    @property
    def session_key(self):
        """Property for accessing the saved session key"""
        if self._session_key:
            return self._session_key

        self._session_key = self._http_response.getheader('x-auth-token')
        return self._session_key

    @property
    def session_location(self):
        """Property for accessing the saved session location"""
        if self._session_location:
            return self._session_location

        self._session_location = self._http_response.getheader('location')
        return self._session_location

    @property
    def request(self):
        """Property for accessing the saved http request"""
        return self._rest_request

    def __str__(self):
        """Class string formatter"""
        headerstr = ''
        for header in self.getheaders():
            headerstr += u'%s %s\n' % (header[0], header[1])

        return u"%(status)s\n%(headerstr)s\n\n%(body)s" % \
            {'status': self.status, 'headerstr': headerstr, \
             'body': self.text.decode('utf-8', 'ignore')}

class JSONEncoder(json.JSONEncoder):
    """JSON Encoder class"""
    def default(self, obj):
        """Set defaults in json encoder class"""
        if isinstance(obj, RestResponse):
            jsondict = OrderedDict()
            jsondict['Status'] = obj.status
            jsondict['Headers'] = list()

            for hdr in obj.getheaders():
                headerd = dict()
                headerd[hdr[0]] = hdr[1]
                jsondict['Headers'].append(headerd)

            if obj.text:
                jsondict['Content'] = obj.dict

            return jsondict

        return json.JSONEncoder.default(self, obj)

class JSONDecoder(json.JSONDecoder):
    """Custom JSONDecoder that understands our types"""
    def decode(self, json_string):
        """Decode json string

        :param json_string: The json string to be decoded into usable data.
        :type json_string: str.

        """
        parsed_dict = super(JSONDecoder, self).decode(json_string)

        return parsed_dict

class _FakeSocket(StringIO):
    """
       slick way to parse a http response.
       http://pythonwise.blogspot.com/2010/02/parse-http-response.html
    """
    def makefile(self, *args, **kwargs):
        """Return self object"""
        return self

class RisRestResponse(RestResponse):
    """Returned by Rest requests from RIS"""
    def __init__(self, rest_request, resp_txt):
        self._respfh = StringIO(resp_txt)
        self._socket = _FakeSocket(self._respfh.read())
        response = httplib.HTTPResponse(self._socket)
        response.begin()
        super(RisRestResponse, self).__init__(rest_request, response)

class StaticRestResponse(RestResponse):
    """A RestResponse object used when data is being cached."""
    def __init__(self, **kwargs):
        restreq = None
        if 'restreq' in kwargs:
            restreq = kwargs['restreq']

        super(StaticRestResponse, self).__init__(restreq, None)

        if 'Status' in kwargs:
            self._status = kwargs['Status']

        if 'Headers' in kwargs:
            self._headers = kwargs['Headers']

        if 'session_key' in kwargs:
            self._session_key = kwargs['session_key']

        if 'session_location' in kwargs:
            self._session_location = kwargs['session_location']

        if 'Content' in kwargs:
            content = kwargs['Content']
            if isinstance(content, basestring):
                self._read = content
            else:
                self._read = json.dumps(content)
        else:
            self._read = ''

    def getheaders(self):
        """Function for accessing the headers"""
        returnlist = list()
        if isinstance(self._headers, dict):
            for key, value in self._headers.iteritems():
                returnlist.append((key, value))
        else:
            for item in self._headers:
                returnlist.append(item.items()[0])

        return returnlist

class AuthMethod(object):
    """AUTH Method class"""
    BASIC = 'basic'
    SESSION = 'session'

class RestClientBase(object):
    """Base class for RestClients"""
    MAX_RETRY = 10

    def __init__(self, base_url, username=None, password=None,
                 default_prefix='/rest/v1', biospassword=None, sessionkey=None):
        """Initialization of the base class RestClientBase

        :param base_url: The url of the remote system
        :type base_url: str
        :param username: The username used for authentication
        :type username: str
        :param password: The password used for authentication
        :type password: str
        :param default_prefix: The default root point
        :type default_prefix: str
        :param biospassword: biospassword for base_url if needed
        :type biospassword: str
        :param sessionkey: sessionkey for the current login of base_url
        :type sessionkey: str

        """

        self.__base_url = base_url
        self.__username = username
        self.__password = password
        self.__biospassword = biospassword
        self.__url = urlparse2.urlparse(base_url)
        self.__session_key = sessionkey
        self.__authorization_key = None
        self.__session_location = None
        self._conn = None
        self._conn_count = 0
        self.login_url = None
        self.default_prefix = default_prefix

        self.__init_connection()
        self.get_root_object()
        self.__destroy_connection()

    def __init_connection(self, url=None):
        """Function for initiating connection with remote server

        :param url: The url of the remote system
        :type url: str

        """
        self.__destroy_connection()

        url = url if url else self.__url
        if url.scheme.upper() == "HTTPS":
            if sys.version_info < (2, 7, 9):
                self._conn = httplib.HTTPSConnection(
                    url.netloc)
            else:
                self._conn = httplib.HTTPSConnection(
                    url.netloc,
                    # pylint: disable=protected-access
                    context=ssl._create_unverified_context())
        elif url.scheme.upper() == "HTTP":
            self._conn = httplib.HTTPConnection(url.netloc)
        else:
            pass

    def __destroy_connection(self):
        """Function for closing connection with remote server"""
        if self._conn:
            self._conn.close()

        self._conn = None
        self._conn_count = 0

    def get_username(self):
        """Return used username"""
        return self.__username

    def set_username(self, username):
        """Set user name

        :param username: The username to be set.
        :type username: str

        """
        self.__username = username

    def get_password(self):
        """Return used password"""
        return self.__password

    def set_password(self, password):
        """Set password

        :param password: The password to be set.
        :type password: str

        """
        self.__password = password

    def get_biospassword(self):
        """Return BIOS password"""
        return self.__biospassword

    def set_biospassword(self, biospassword):
        """Set BIOS password

        :param biospassword: The biospassword to be set.
        :type biospassword: str

        """
        self.__biospassword = biospassword

    def get_base_url(self):
        """Return used url"""
        return self.__base_url

    def set_base_url(self, url):
        """Set based url

        :param url: The url to be set.
        :type url: str

        """
        self.__base_url = url

    def get_session_key(self):
        """Return session key"""
        return self.__session_key

    def set_session_key(self, session_key):
        """Set session key

        :param session_key: The session_key to be set.
        :type session_key: str

        """
        self.__session_key = session_key

    def get_session_location(self):
        """Return session location"""
        return self.__session_location

    def set_session_location(self, session_location):
        """Set session location

        :param session_location: The session_location to be set.
        :type session_location: str

        """
        self.__session_location = session_location

    def get_authorization_key(self):
        """Return authorization key"""
        return self.__authorization_key

    def set_authorization_key(self, authorization_key):
        """Set authorization key

        :param session_location: The session_location to be set.
        :type session_location: str

        """
        self.__authorization_key = authorization_key

    def get_root_object(self):
        """Perform an initial get and store the result"""
        try:
            resp = self.get('%s%s' % (self.__url.path, self.default_prefix))
        except Exception:
            raise

        if resp.status != 200:
            raise ServerDownOrUnreachableError("Server not reachable, iLO " \
                                               "return code: %d" % resp.status)

        content = resp.text
        root_data = None

        try:
            root_data = json.loads(content, "ISO-8859-1")
        except ValueError, excp:
            LOGGER.error(u"%s for JSON content %s", excp, content)
            raise

        self.root = RisObject.parse(root_data)
        self.root_resp = resp

    def get(self, path, args=None, headers=None):
        """Perform a GET request

        :param path: the URL path.
        :param path: str.
        :params args: the arguments to get.
        :params args: dict.

        """
        return self._rest_request(path, method='GET', args=args, headers=headers)

    def post(self, path, args=None, body=None, providerheader=None,
             headers=None):
        """Perform a POST request

        :param path: the URL path.
        :param path: str.
        :params args: the arguments to post.
        :params args: dict.
        :param body: the body to the sent.
        :type body: str.
        :param provideheader: provider id for the header.
        :type providerheader: str.

        """
        return self._rest_request(path, method='POST', args=args, body=body,
                                  providerheader=providerheader,
                                  headers=headers)

    def put(self, path, args=None, body=None, optionalpassword=None,
            providerheader=None, headers=None):
        """Perform a PUT request

        :param path: the URL path.
        :type path: str.
        :param args: the arguments to put.
        :type args: dict.
        :param body: the body to the sent.
        :type body: str.
        :param optionalpassword: provide password for authentication.
        :type optionalpassword: str.
        :param provideheader: provider id for the header.
        :type providerheader: str.

        """
        return self._rest_request(path, method='PUT', args=args, body=body,
                                  optionalpassword=optionalpassword,
                                  providerheader=providerheader, headers=headers)

    def patch(self, path, args=None, body=None, optionalpassword=None,
              providerheader=None, headers=None):
        """Perform a PUT request

        :param path: the URL path.
        :type path: str.
        :param args: the arguments to patch.
        :type args: dict.
        :param body: the body to the sent.
        :type body: str.
        :param optionalpassword: provide password for authentication.
        :type optionalpassword: str.
        :param provideheader: provider id for the header.
        :type providerheader: str.

        """
        return self._rest_request(path, method='PATCH', args=args, body=body,
                                  optionalpassword=optionalpassword,
                                  providerheader=providerheader, headers=headers)


    def delete(self, path, args=None, optionalpassword=None,
               providerheader=None, headers=None):
        """Perform a DELETE request

        :param path: the URL path.
        :type path: str.
        :param args: the arguments to delete.
        :type args: dict.
        :param optionalpassword: provide password for authentication.
        :type optionalpassword: str.
        :param provideheader: provider id for the header.
        :type providerheader: str.

        """
        return self._rest_request(path, method='DELETE', args=args,
                                  optionalpassword=optionalpassword,
                                  providerheader=providerheader,
                                  headers=headers)

    def _get_req_headers(self, headers=None, providerheader=None,
                         optionalpassword=None):
        """Get the request headers

        :param headers: additional headers to be utilized
        :type headers: str
        :param provideheader: provider id for the header.
        :type providerheader: str.
        :param optionalpassword: provide password for authentication.
        :type optionalpassword: str.

        """
        headers = headers if isinstance(headers, dict) else dict()

        if providerheader:
            headers['X-CHRP-RIS-Provider-ID'] = providerheader

        if self.__biospassword:
            hash_object = hashlib.sha256(self.__biospassword)
            headers['X-HPRESTFULAPI-AuthToken'] = \
                                                hash_object.hexdigest().upper()
        elif optionalpassword:
            hash_object = hashlib.sha256(optionalpassword)
            headers['X-HPRESTFULAPI-AuthToken'] = \
                                                hash_object.hexdigest().upper()

        if self.__session_key:
            headers['X-Auth-Token'] = self.__session_key
        elif self.__authorization_key:
            headers['Authorization'] = self.__authorization_key

        headers['Accept'] = '*/*'
        headers['Connection'] = 'Keep-Alive'

        return headers

    def _rest_request(self, path, method='GET', args=None, body=None,
                      headers=None, optionalpassword=None,
                      providerheader=None):
        """Rest request main function

        :param path: path within tree
        :type path: str
        :param method: method to be implemented
        :type method: str
        :param args: the arguments for method
        :type args: dict
        :param body: body payload for the rest call
        :type body: dict
        :param headers: provide additional headers
        :type headers: dict
        :param optionalpassword: provide password for authentication
        :type optionalpassword: str
        :param provideheader: provider id for the header
        :type providerheader: str

        """
        headers = self._get_req_headers(headers, providerheader, \
                                                            optionalpassword)
        reqpath = path.replace('//', '/')

        if body:
            if isinstance(body, dict) or isinstance(body, list):
                headers['Content-Type'] = u'application/json'
                body = json.dumps(body)
            else:
                headers['Content-Type'] = u'application/x-www-form-urlencoded'
                body = urllib.urlencode(body)

            if method == 'PUT':
                resp = self._rest_request(path=path)
                try:
                    if resp.getheader('content-encoding') == 'gzip':
                        buf = StringIO()
                        gfile = gzip.GzipFile(mode='wb', fileobj=buf)

                        try:
                            gfile.write(str(body))
                        finally:
                            gfile.close()

                        compresseddata = buf.getvalue()
                        if compresseddata:
                            data = bytearray()
                            data.extend(buffer(compresseddata))
                            body = data
                except BaseException as excp:
                    LOGGER.error('Error occur while compressing body: %s', excp)
                    raise

            headers['Content-Length'] = len(body)

        if args:
            if method == 'GET':
                reqpath += '?' + urllib.urlencode(args)
            elif method == 'PUT' or method == 'POST' or method == 'PATCH':
                headers['Content-Type'] = u'application/x-www-form-urlencoded'
                body = urllib.urlencode(args)

        restreq = RestRequest(reqpath, method=method, body=body)

        attempts = 0
        while attempts < self.MAX_RETRY:

            if logging.getLogger().isEnabledFor(logging.DEBUG):
                LOGGER.debug('REQ %s', (restreq))

            attempts = attempts + 1

            try:
                while True:
                    if self._conn is None:
                        self.__init_connection()

                    self._conn.request(method.upper(), reqpath, body=body, \
                                                                headers=headers)
                    self._conn_count += 1
                    resp = self._conn.getresponse()

                    if resp.getheader('Connection') == 'close':
                        self.__destroy_connection()
                    if resp.status not in range(300, 399):
                        break

                    newloc = resp.getheader('location')
                    newurl = urlparse2.urlparse(newloc)
                    reqpath = newurl.path
                    self.__init_connection(newurl)

                restresp = RestResponse(restreq, resp)

                try:
                    if restresp.getheader('content-encoding') == "gzip":
                        compressedfile = StringIO(restresp.text)
                        decompressedfile = gzip.GzipFile(fileobj=compressedfile)
                        restresp.text = decompressedfile.read()
                except Exception as excp:
                    LOGGER.error('Error occur while decompressing body: %s', \
                                                                        excp)
                    raise DecompressResponseError()
            except Exception as excp:
                if isinstance(excp, DecompressResponseError):
                    raise

                LOGGER.info('Retrying [%s]', excp)
                time.sleep(1)

                self.__init_connection()
                continue
            else:
                break

        self.__destroy_connection()
        if attempts < self.MAX_RETRY:

            if logging.getLogger().isEnabledFor(logging.DEBUG):
                LOGGER.debug('RESP %s', (restresp))

            return restresp
        else:
            raise RetriesExhaustedError()

    def login(self, username=None, password=None, auth=AuthMethod.BASIC):
        """Login and start a REST session.  Remember to call logout() when"""
        """ you are done.

        :param username: the iLO username.
        :type username: str.
        :param password: the iLO password.
        :type password: str.
        :param auth: authentication method
        :type auth: object/instance of class AuthMethod

        """

        self.__username = username if username else self.__username
        self.__password = password if password else self.__password

        if auth == AuthMethod.BASIC:
            auth_key = base64.b64encode(
                ('%s:%s' % (self.__username,
                            self.__password)).encode('utf-8')).decode('utf-8')
            self.__authorization_key = u'Basic %s' % auth_key

            headers = dict()
            headers['Authorization'] = self.__authorization_key

            respvalidate = self._rest_request(
                '%s%s' % (self.__url.path, self.login_url),
                headers=headers)

            if respvalidate.status == 401:
                raise InvalidCredentialsError(\
                    self.root.Oem.Hp.Sessions.LoginFailureDelay)
        elif auth == AuthMethod.SESSION:
            data = dict()
            data['UserName'] = self.__username
            data['Password'] = self.__password

            headers = dict()
            resp = self._rest_request(self.login_url, method="POST", \
                                      body=data, headers=headers)

            LOGGER.info(json.loads(u'%s' % resp.text))
            LOGGER.info('Login returned code %s: %s', resp.status, resp.text)

            self.__session_key = resp.session_key
            self.__session_location = resp.session_location
            if not self.__session_key and not resp.status == 200:
                raise InvalidCredentialsError(
                    self.root.Oem.Hp.Sessions.LoginFailureDelay)
            else:
                self.set_username(None)
                self.set_password(None)
        else:
            pass

    def logout(self):
        """ Logout of session. YOU MUST CALL THIS WHEN YOU ARE DONE TO FREE"""
        """ UP SESSIONS"""
        if self.__session_key:
            if self.__base_url == "blobstore://.":
                session_loc = self.__session_location.replace("https://", '')
                session_loc = session_loc.replace(' ', '%20')
            else:
                session_loc = self.__session_location.replace(self.__base_url, '')

            resp = self.delete(session_loc)
            LOGGER.info("User logged out: %s", resp.text)

            self.__session_key = None
            self.__session_location = None
            self.__authorization_key = None
        return

class HttpClient(RestClientBase):
    """A client for Rest"""
    def __init__(self, base_url, username=None, password=None, \
                 default_prefix='/rest/v1', biospassword=None, \
                 sessionkey=None, is_redfish=False):
        self.is_redfish = is_redfish
        super(HttpClient, self).__init__(base_url, username=username, \
                             password=password, default_prefix=default_prefix, \
                             biospassword=biospassword, sessionkey=sessionkey)

        if self.is_redfish:
            self.login_url = self.root.Links.Sessions['@odata.id']
        else:
            self.login_url = self.root.links.Sessions.href

    def _rest_request(self, path='', method="GET", args=None, body=None,
                      headers=None, optionalpassword=None, providerheader=None):
        """Rest request for http client

        :param path: path within tree
        :type path: str
        :param method: method to be implemented
        :type method: str
        :param args: the arguments for method
        :type args: dict
        :param body: body payload for the rest call
        :type body: dict
        :param headers: provide additional headers
        :type headers: dict
        :param optionalpassword: provide password for authentication
        :type optionalpassword: str
        :param provideheader: provider id for the header
        :type providerheader: str

        """
        if (not self.is_redfish and
                self.default_prefix in path and path[-1] == '/'):
            path = path[0:-1]
        elif (self.is_redfish and
              self.default_prefix in path and path[-1] != '/'):
            path = path + '/'
        else:
            pass

        return super(HttpClient, self)._rest_request(path=path, method=method, \
                                     args=args, body=body, headers=headers, \
                                     optionalpassword=optionalpassword, \
                                     providerheader=providerheader)

    def _get_req_headers(self, headers=None, providerheader=None, \
                                                        optionalpassword=None):
        """Get the request headers for http client

        :param headers: additional headers to be utilized
        :type headers: str
        :param provideheader: provider id for the header
        :type providerheader: str
        :param optionalpassword: provide password for authentication
        :type optionalpassword: str

        """
        headers = super(HttpClient, self)._get_req_headers(headers,
                                                           providerheader,
                                                           optionalpassword)
        if self.is_redfish:
            headers['OData-Version'] = '4.0'

        return headers

class Blobstore2RestClient(RestClientBase):
    """A client for Rest that uses the blobstore2 as the transport"""
    _http_vsn_str = 'HTTP/1.1'

    def __init__(self, base_url, default_prefix='/rest/v1', username=None,
                 password=None, sessionkey=None, is_redfish=False):
        self.is_redfish = is_redfish
        super(Blobstore2RestClient, self).__init__(base_url, \
                                            username=username, \
                                            password=password, \
                                            default_prefix=default_prefix, \
                                            sessionkey=sessionkey)

        self._method = None
        if self.is_redfish:
            self.login_url = self.root.Links.Sessions['@odata.id']
        else:
            self.login_url = self.root.links.Sessions.href

    def _rest_request(self, path='', method="GET", args=None, body=None,
                      headers=None, optionalpassword=None,
                      providerheader=None):
        """Rest request for blob store client

        :param path: path within tree
        :type path: str
        :param method: method to be implemented
        :type method: str
        :param args: the arguments for method
        :type args: dict
        :param body: body payload for the rest call
        :type body: dict
        :param headers: provide additional headers
        :type headers: dict
        :param optionalpassword: provide password for authentication
        :type optionalpassword: str
        :param provideheader: provider id for the header
        :type providerheader: str

        """
        headers = self._get_req_headers(headers, providerheader,
                                        optionalpassword)

        if (not self.is_redfish and
                self.default_prefix in path and path[-1] == '/'):
            path = path[0:-1]
        elif (self.is_redfish and
              self.default_prefix in path and path[-1] != '/'):
            path = path + '/'
        else:
            pass

        reqpath = path.replace('//', '/')

        if body:
            if isinstance(body, dict) or isinstance(body, list):
                headers['Content-Type'] = u'application/json'
                body = json.dumps(body)
            else:
                headers['Content-Type'] = u'application/x-www-form-urlencoded'
                body = urllib.urlencode(body)

            if method == 'PUT':
                resp = self._rest_request(path=path)

                try:
                    if resp.getheader('content-encoding') == 'gzip':
                        buf = StringIO()
                        gfile = gzip.GzipFile(mode='wb', fileobj=buf)

                        try:
                            gfile.write(str(body))
                        finally:
                            gfile.close()

                        compresseddata = buf.getvalue()
                        if compresseddata:
                            data = bytearray()
                            data.extend(buffer(compresseddata))
                            body = data
                except BaseException as excp:
                    LOGGER.error('Error occur while compressing body: %s', excp)
                    raise

            headers['Content-Length'] = len(body)

        self._method = method
        str1 = '%s %s %s\r\n' % (method, reqpath,\
                                Blobstore2RestClient._http_vsn_str)

        str1 += 'Host: \r\n'
        str1 += 'Accept-Encoding: identity\r\n'
        for header, value in headers.iteritems():
            str1 += '%s: %s\r\n' % (header, value)

        str1 += '\r\n'

        if body and len(body) > 0:
            if isinstance(body, bytearray):
                str1 = str1.encode("ASCII") + body
            else:
                str1 += body

        bs2 = BlobStore2()
        if not isinstance(str1, bytearray):
            str1 = str1.encode("ASCII")

        resp_txt = bs2.rest_immediate(str1)

        #Dummy response to support a bad host response
        if len(resp_txt) == 0:
            resp_txt = "HTTP/1.1 500 Not Found\r\nAllow: " \
            "GET\r\nCache-Control: no-cache\r\nContent-length: " \
            "0\r\nContent-type: text/html\r\nDate: Tues, 1 Apr 2025 " \
            "00:00:01 GMT\r\nServer: " \
            "HP-iLO-Server/1.30\r\nX_HP-CHRP-Service-Version: 1.0.3\r\n\r\n\r\n"

        restreq = RestRequest(reqpath, method=method, body=body)
        rest_response = RisRestResponse(restreq, resp_txt)

        try:
            if rest_response.getheader('content-encoding') == 'gzip':
                compressedfile = StringIO(rest_response.text)
                decompressedfile = gzip.GzipFile(fileobj=compressedfile)
                rest_response.text = decompressedfile.read()
        except StandardError:
            pass

        if rest_response.status in range(300, 399):
            newloc = rest_response.getheader("location")
            newurl = urlparse2.urlparse(newloc)

            rest_response = self._rest_request(newurl.path, \
                               method, args, body, headers, \
                               optionalpassword, providerheader)

        return rest_response

    def _get_req_headers(self, headers=None, providerheader=None, \
                                                optionalpassword=None):
        """Get the request headers for blob store client

        :param headers: additional headers to be utilized
        :type headers: str
        :param provideheader: provider id for the header
        :type providerheader: str
        :param optionalpassword: provide password for authentication
        :type optionalpassword: str

        """
        headers = super(Blobstore2RestClient,
                        self)._get_req_headers(headers,
                                               providerheader,
                                               optionalpassword)
        if self.is_redfish:
            headers['OData-Version'] = '4.0'

        return headers

def get_client_instance(base_url=None, username=None, password=None,
                        default_prefix='/rest/v1', biospassword=None,
                        sessionkey=None, is_redfish=False):
    """Create and return appropriate RESTful/REDFISH client instance."""
    """ Instantiates appropriate Rest/Redfish object based on existing"""
    """ configuration. Use this to retrieve a pre-configured Rest object

    :param base_url: rest host or ip address.
    :type base_url: str.
    :param username: username required to login to server
    :type: str
    :param password: password credentials required to login
    :type password: str
    :param default_prefix: default root to extract tree
    :type default_prefix: str
    :param biospassword: BIOS password for the server if set
    :type biospassword: str
    :param sessionkey: session key credential for current login
    :type sessionkey: str
    :param is_redfish: If True, a Redfish specific header (OData) will be added to every request
    :type is_redfish: boolean
    :returns: a client object. Either HTTP or Blobstore.

    """
    if not base_url or base_url.startswith('blobstore://'):
        if platform.system() == 'Windows':
            if not ctypes.windll.kernel32.LoadLibraryA('cpqci'):
                raise ChifDriverMissingOrNotFound()
        else:
            if not os.path.isdir('/dev/hpilo'):
                raise ChifDriverMissingOrNotFound()

        return Blobstore2RestClient(base_url=base_url, default_prefix=default_prefix,
                                    username=username, password=password,
                                    sessionkey=sessionkey, is_redfish=is_redfish)
    else:
        return HttpClient(base_url=base_url, username=username, password=password,
                          default_prefix=default_prefix,
                          biospassword=biospassword, sessionkey=sessionkey,
                          is_redfish=is_redfish)

