from functools import partial
from random import randint
import re
import urllib
import urlparse

import requests

from django.conf import settings

from .endpoints import ENDPOINTS


class ApiChunk(object):
    def __init__(self, name):
        self.name = name

    def __getattr__(self, name):
        new_name = '__'.join([self.name, name])
        return ApiChunk(new_name)

    def __call__(self, *args, **kwargs):
        many = kwargs.pop('many', False)

        request = partial(
            getattr(requests.api, 'get'),  # TODO Generalize
            auth=requests.auth.HTTPBasicAuth(*settings.RBX_CREDENTIALS),
        )

        url_kwarg_keys = re.findall('{([^}]*)}', ENDPOINTS[self.name])
        url_kwargs = dict((key, kwargs.pop(key, None))
                          for key in url_kwarg_keys)

        url = urlparse.urljoin(
            settings.RBX_HOST,
            ENDPOINTS[self.name].format(*args, **url_kwargs)
        )

        url_parts = list(urlparse.urlparse(url))
        query = dict(urlparse.parse_qsl(url_parts[4]))  # URL params
        query.update(kwargs)
        url_parts[4] = urllib.urlencode(query)

        url = urlparse.urlunparse(url_parts)

        response = request(url).json()

        if many:
            # TODO make sure we've only got one result
            return response['results'][0]
        else:
            return response


class Client(object):
    methods = ('post', 'patch', 'put', 'delete', 'get', 'head', 'options')

    def __getattr__(self, name):

        return ApiChunk(name)


def get_script_path(campaign_id, creative_id, site_id,
                    placement_id, view_event=True):
    """
    Returns the location of live ad scripts.
    If we don't want to fire the view event, then we link
    straight to the ad.js in S3 otherwise we hit the
    adservers as usual.
    """
    if view_event:
        return '/'.join([
            settings.LIVE_SERVING_LOCATION,
            get_random_sixteen_digit(),
            str(campaign_id), str(creative_id),
            str(site_id), str(placement_id),
        ])
    else:
        return '/'.join([
            settings.AWS_SERVING_LOCATION,
            str(campaign_id), str(placement_id),
            'ad.js',
        ])


def get_random_sixteen_digit():
    """
    Simulates the javascript random 16 digit number
    generation we use for cache busting.
    """
    return ''.join(["%s" % randint(0, 9) for num in range(16)])
