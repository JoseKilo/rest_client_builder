from functools import partial
import json
import re
import urllib
import urlparse

import requests
from requests.auth import AuthBase, HTTPBasicAuth

from .endpoints import ENDPOINTS


JSON_HEADERS = {'Content-type': 'application/json'}


class HTTPAuthorizationHeaderAuth(AuthBase):

    def __init__(self, authorization):
        self.authorization = authorization

    def __call__(self, request):
        request.headers['Authorization'] = self.authorization
        return request


class ApiChunk(object):
    """
    Abstractions of an Api endpoint or an Api midpoint.

    For an API endpoint like 'api/shutters/shutterscreative-list'
    Client library users will invoke Client().shutters.shutterscreative_list()
    Where each midpoint in the chain will be an instance of this class.

    This class instances are callables that will perform HTTP requests
    when called.

    Instances of this class can also return new instances if nested api
    resources are invoked.
    """

    def __init__(self, base_url, auth, name, headers):
        self.name = name
        self.base_url = base_url
        self.auth = auth
        self.headers = headers

    def __getattr__(self, name):
        if name.startswith('__'):
            return object.__getattribute__(self, name)
        else:
            new_name = '__'.join([self.name, name])
            return ApiChunk(
                self.base_url, self.auth, new_name, self.headers
            )

    def __url(self, *args, **kwargs):
        """
        Construct the url
        """
        return urlparse.urljoin(
            self.base_url,
            ENDPOINTS[self.name].format(*args, **kwargs)
        )

    def __get_request(self, method):
        if self.auth is None:
            return getattr(requests.api, method)
        return partial(getattr(requests.api, method), auth=self.auth)

    def __call__(self, *args, **kwargs):
        """
        Within kwargs we can receive url parameters (which need to be used
        to construct the url structure and they are mandatory) and also
        extra GET parameters (which are appended at the end).

        If an extra argument 'http_method' is passed, it will be used
        instead of GET. This can be useful to perform POST requests that
        return some information and we want that information to be available
        (as an opposite to the __setattr__ syntax).

        Another extra argument `http_body` can be used. Its value will be
        encoded as JSON and sent as the request body.
        """

        # Look for a 'http_method' to use
        http_method = kwargs.pop('http_method', 'get')
        http_body = kwargs.pop('http_body', None)

        request = self.__get_request(http_method)

        # Regular expression to split both types of parameters
        url_kwarg_keys = re.findall('{([^}]*)}', ENDPOINTS[self.name])
        url_kwargs = dict((key, kwargs.pop(key, None))
                          for key in url_kwarg_keys)

        # Construct the url
        url = self.__url(*args, **url_kwargs)

        # Append extra parameters
        url_parts = list(urlparse.urlparse(url))
        query = dict(urlparse.parse_qsl(url_parts[4]))  # URL params
        query.update(kwargs)
        url_parts[4] = urllib.urlencode(query)

        url = urlparse.urlunparse(url_parts)
        # append headers passed to the Client
        JSON_HEADERS.update(self.headers)
        request_kwargs = {'url': url, 'headers': JSON_HEADERS}
        if http_body is not None:
            request_kwargs['data'] = json.dumps(http_body)

        response = request(**request_kwargs)
        if response.status_code >= 400:
            raise ValueError('Url: {}, HTTP Status: {}, Response: {}'.format(
                url,
                response.status_code,
                response.content
            ))

        response_json = response.json()
        return response_json

    def __setattr__(self, name, value):
        """
        Used to produce a POST request. Value will contain a dictionary with
        the arguments to encode.
        """
        if name in ('name', 'base_url', 'auth', 'headers'):
            self.__dict__[name] = value
            return

        request = self.__get_request('post')

        last_chunk = self.__getattr__(name)
        url = last_chunk.__url()

        response = request(url, data=value, headers=JSON_HEADERS)
        if response.status_code >= 400:
            raise ValueError('Url: {}, HTTP Status: {}, Response: {}'.format(
                url,
                response.status_code,
                response.content
            ))


class Client(object):
    """
    Object used to generate API calls from the user code.

    Usage:

        client = Client(
            base_url='http://www.my-domain.com/api',
            username='ApiUser',
            password='ApiPassword'
        )
        result = client.my_api_resource.my_api_sub_resource(id=42, name='This')
    """

    methods = ('post', 'patch', 'put', 'delete', 'get', 'head', 'options')

    def __init__(self, base_url, username=None, password=None,
                 authorization=None, headers={}):
        """
        :param base_url: Base url used to build API requests
        :param username: Username used to authenticate
        :param password: Password used to authenticate
        :param authorization: Token used as an Authorization HTTP header
        :param custom_headers: Headers to be included in a response
        """
        self._base_url = base_url
        if username is not None and password is not None:
            self._auth = HTTPBasicAuth(username, password)
        elif authorization is not None:
            self._auth = HTTPAuthorizationHeaderAuth(authorization)
        else:
            self._auth = None
        self._headers = headers

    def __getattr__(self, name):
        return ApiChunk(self._base_url, self._auth, name, self._headers)
