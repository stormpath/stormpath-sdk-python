# -*- coding: utf-8 -*-
import unittest
from .test_base import BaseTest
import httpretty
from httpretty import HTTPretty
import json

from stormpath.resource import CustomData


class TestAccount(BaseTest):

    @httpretty.activate
    def test_properties(self):

        httpretty.register_uri(
            httpretty.GET,
            self.base_href + "/tenants/current",
            location=self.tenant_href,
            status=302)

        httpretty.register_uri(
            httpretty.GET,
            self.tenant_href,
            body=json.dumps(self.tenant_body),
            content_type="application/json")

        httpretty.register_uri(
            httpretty.GET,
            self.custom_href,
            body=json.dumps(self.custom_body),
            content_type="application/json")

        custom_data = CustomData(self.client, href=self.custom_href)

        self.assertEqual(custom_data['rank'], self.custom_body['rank'])
        self.assertEqual(
            custom_data['birthDate'], self.custom_body['birthDate'])
        self.assertEqual(
            custom_data['birthPlace'], self.custom_body['birthPlace'])
        self.assertEqual(
            custom_data['favoriteDrink'], self.custom_body['favoriteDrink'])
        self.assertEqual(custom_data.created_at, self.custom_body['createdAt'])

        with self.assertRaises(KeyError):
            custom_data['createdAt']

        with self.assertRaises(KeyError):
            custom_data['created_at']

        self.assertEqual(HTTPretty.last_request.path, self.custom_path)

    @httpretty.activate
    def test_delete(self):
        httpretty.register_uri(
            httpretty.GET,
            self.base_href + "/tenants/current",
            location=self.tenant_href,
            status=302)

        httpretty.register_uri(
            httpretty.GET,
            self.tenant_href,
            body=json.dumps(self.tenant_body),
            content_type="application/json")

        httpretty.register_uri(
            httpretty.GET,
            self.custom_href,
            body=json.dumps(self.custom_body),
            content_type="application/json")

        httpretty.register_uri(
            httpretty.POST,
            self.custom_href,
            body=json.dumps({}),
            content_type="application/json")

        httpretty.register_uri(
            httpretty.DELETE,
            self.custom_href,
            body='', status=204)

        custom_data = CustomData(self.client, href=self.custom_href)
        custom_data.delete()

        self.assertEqual(HTTPretty.last_request.method, 'DELETE')
        self.assertEqual(HTTPretty.last_request.path, self.custom_path)

        httpretty.register_uri(
            httpretty.DELETE,
            self.custom_href + '/rank',
            body='', status=204)

        del custom_data['rank']
        self.assertEqual(HTTPretty.last_request.method, 'GET')
        self.assertEqual(HTTPretty.last_request.path, self.custom_path)
        custom_data.save()
        self.assertEqual(HTTPretty.last_request.method, 'POST')
        self.assertEqual(HTTPretty.last_request.path, self.custom_path)

    @httpretty.activate
    def test_update(self):
        httpretty.register_uri(
            httpretty.GET,
            self.base_href + "/tenants/current",
            location=self.tenant_href,
            status=302)

        httpretty.register_uri(
            httpretty.GET,
            self.tenant_href,
            body=json.dumps(self.tenant_body),
            content_type="application/json")

        httpretty.register_uri(
            httpretty.GET,
            self.custom_href,
            body=json.dumps(self.dir_body),
            content_type="application/json")

        httpretty.register_uri(
            httpretty.POST,
            self.custom_href,
            body=json.dumps(self.custom_body),
            content_type="application/json")

        custom_data = CustomData(self.client, href=self.custom_href)
        custom_data['rank'] = 'Admiral'
        custom_data.save()

        self.assertEqual(HTTPretty.last_request.method, 'POST')
        self.assertEqual(HTTPretty.last_request.path, self.custom_path)

if __name__ == '__main__':
    unittest.main()
