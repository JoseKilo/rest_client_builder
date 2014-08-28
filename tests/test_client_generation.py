from unittest import TestCase

from rest_client.management.commands.generate_api_client import clean_patterns


class ClientGenerationTest(TestCase):

    def test_clean_patterns_with_normal_pk(self):
        """
        Clean an URL with the typical pk-based pattern
        """
        urls_data = [
            (lambda _: None,  # View
             'api/things/thing/(?P<pk>[^/]+)/$',
             'things:thing-detail')
        ]

        result = clean_patterns(urls_data)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], 'things__thing_detail')
        self.assertEqual(result[0][1], 'api/things/thing/{pk}/')

    def test_clean_patterns_with_data_type(self):
        """
        Clean an URL containing an argument with a data type
        """
        urls_data = [
            (lambda _: None,  # View,
             '^bakery/bake/(?P<thing_id>\\d+)/',
             'bakery:bake')
        ]

        result = clean_patterns(urls_data)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], 'bakery__bake')
        self.assertEqual(result[0][1], 'bakery/bake/{thing_id}')
