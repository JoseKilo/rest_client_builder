import json
from unittest import TestCase
import urllib

import httpretty

import rest_client
from rest_client.client import Client


class RestClientTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super(RestClientTest, cls).setUpClass()

        rest_client.client.ENDPOINTS = {
            'end__point': 'end/point/'
        }

        cls.client = Client('http://no.com', 'us3er', 'p4ssw0rd')

    @httpretty.activate
    def test_client_get(self):
        httpretty.register_uri(
            httpretty.GET, 'http://no.com/end/point/',
            body='{"name": "object_name"}',
            content_type="application/json"
        )

        response = self.client.end.point()

        self.assertEquals(response['name'], 'object_name')
        self.assertEquals(httpretty.last_request().method, httpretty.GET)

    @httpretty.activate
    def test_client_post(self):
        httpretty.register_uri(
            httpretty.POST, 'http://no.com/end/point/',
            body='{"name": "object_name"}',
            status=201,  # Resource created
            content_type="application/json"
        )

        self.client.end.point = {'name': 'custom_name'}

        self.assertEquals(httpretty.last_request().method, httpretty.POST)

    @httpretty.activate
    def test_client_post_invalid_request(self):
        httpretty.register_uri(
            httpretty.POST, 'http://no.com/end/point/',
            body='{"name": "That name already exists"}',
            status=400,  # Invalid request
            content_type="application/json"
        )

        try:
            self.client.end.point = {'name': 'custom_name'}
            self.assertFail()
        except Exception as exc:
            self.assertEquals(
                exc.message,
                ('Url: http://no.com/end/point/, HTTP Status: 400, '
                 'Response: {"name": "That name already exists"}')
            )

        self.assertEquals(httpretty.last_request().method, httpretty.POST)

    @httpretty.activate
    def test_client_post_with_call_syntax(self):
        httpretty.register_uri(
            httpretty.POST, 'http://no.com/end/point/',
            body='{"name": "object_name"}',
            status=201,  # Resource created
            content_type="application/json"
        )

        result = self.client.end.point(name='custom_name', http_method='post')

        self.assertEquals(result['name'], 'object_name')
        self.assertEquals(httpretty.last_request().method, httpretty.POST)

    @httpretty.activate
    def test_client_post_invalid_request_with_call_syntax(self):
        httpretty.register_uri(
            httpretty.POST, 'http://no.com/end/point/',
            body='{"name": "That name already exists"}',
            status=400,  # Invalid request
            content_type="application/json"
        )

        try:
            self.client.end.point(http_method='post', name='custom_name')
            self.assertFail()
        except Exception as exc:
            self.assertEquals(
                exc.message,
                ('Url: http://no.com/end/point/?name=custom_name, '
                 'HTTP Status: 400, '
                 'Response: {"name": "That name already exists"}')
            )

        self.assertEquals(httpretty.last_request().method, httpretty.POST)

    @httpretty.activate
    def test_client_post_with_call_syntax_and_http_body(self):
        httpretty.register_uri(
            httpretty.POST, 'http://no.com/end/point/',
            body='{"name": "object_name"}',
            status=201,  # Resource created
            content_type="application/json"
        )

        result = self.client.end.point(http_method='post', http_body={
            'name': 'Some Random Name'
        })

        http_body = urllib.unquote_plus(httpretty.last_request().body)
        http_body_json = json.loads(http_body)
        self.assertEquals(http_body_json['name'], 'Some Random Name')
        self.assertEquals(result['name'], 'object_name')
        self.assertEquals(httpretty.last_request().method, httpretty.POST)
