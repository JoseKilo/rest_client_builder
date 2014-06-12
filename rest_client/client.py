from functools import partial
from random import randint
import re
import urllib
import urlparse

import requests

from .endpoints import ENDPOINTS


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

    def __init__(self, host, credentials, name):
        self.name = name
        self.host = host
        self.credentials = credentials

    def __getattr__(self, name):
        new_name = '__'.join([self.name, name])
        return ApiChunk(self.host, self.credentials, new_name)

    def __call__(self, *args, **kwargs):
        """
        Within kwargs we can receive url parameters (which need to be used
        to construct the url structure and they are mandatory) and also
        extra GET parameters (which are appended at the end).

        """

        request = partial(
            getattr(requests.api, 'get'),  # TODO Generalize
            auth=requests.auth.HTTPBasicAuth(*self.credentials),
        )

        # Regular expression to split both types of parameters
        url_kwarg_keys = re.findall('{([^}]*)}', ENDPOINTS[self.name])
        url_kwargs = dict((key, kwargs.pop(key, None))
                          for key in url_kwarg_keys)

        # Construct the url
        url = urlparse.urljoin(
            self.host,
            ENDPOINTS[self.name].format(*args, **url_kwargs)
        )

        # Append extra parameters
        url_parts = list(urlparse.urlparse(url))
        query = dict(urlparse.parse_qsl(url_parts[4]))  # URL params
        query.update(kwargs)
        url_parts[4] = urllib.urlencode(query)

        url = urlparse.urlunparse(url_parts)

        response = request(url).json()

        return response


class Client(object):
    methods = ('post', 'patch', 'put', 'delete', 'get', 'head', 'options')

    def __init__(self, host, credentials):
        self.host = host
        self.credentials = credentials

    def __getattr__(self, name):
        return ApiChunk(self.host, self.credentials, name)
