"""Unit tests for merchants_view.py."""

import datetime
import json
from typing import List
from unittest.mock import patch

from django.test import Client
from django_opensearch_toolkit.unittest import MagicMockOpenSearchTestCase


class MerchantViewTests(MagicMockOpenSearchTestCase):
    """Tests for the MerchantView class."""

    def connections_to_patch(self) -> List[str]:
        return ["sample_app"]

    def setUp(self) -> None:
        super().setUp()

        self.rest_client = Client()
        self.rest_endpoint = "/api/v1/merchants/"
        self.os_client = self.get_test_client("sample_app")

    def test_get_merchants(self) -> None:
        # Patch the OpenSearch search method
        self.os_client.search.return_value = {
            "hits": {
                "hits": [
                    {
                        "_id": "1",
                        "_source": {
                            "name": "Merchant 1",
                            "description": "Description 1",
                            "website": "http://example1.com",
                        },
                    },
                    {
                        "_id": "2",
                        "_source": {
                            "name": "Merchant 2",
                            "description": "Description 2",
                            "website": "http://example2.com",
                        },
                    },
                ]
            }
        }

        # Call our API
        response = self.rest_client.get(self.rest_endpoint)

        # Check API response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "merchants": [
                    {
                        "id": "1",
                        "name": "Merchant 1",
                        "description": "Description 1",
                        "website": "http://example1.com",
                    },
                    {
                        "id": "2",
                        "name": "Merchant 2",
                        "description": "Description 2",
                        "website": "http://example2.com",
                    },
                ]
            },
        )

        # Check OpenSearch client call
        self.os_client.search.assert_called_once_with(
            index=["merchants"],
            body={
                "query": {"match_all": {}},
                "_source": ["_id", "name", "description", "website"],
                "sort": ["name"],
                "size": 10,
            },
        )

    def test_post_merchant(self) -> None:
        # Patch the OpenSearch index method
        self.os_client.index.return_value = {"_id": "zyrTds13x", "result": "created"}

        # Call our API
        with patch("time.time", return_value=1733088413.532):
            response = self.rest_client.post(
                path=self.rest_endpoint,
                data=json.dumps(
                    {
                        "name": "New Merchant",
                        "description": "New Description",
                        "website": "http://newmerchant.com",
                    }
                ),
                content_type="application/json",
            )

        # Check API response
        self.assertEqual(response.status_code, 201)
        self.assertIn("merchant", response.json())
        self.assertEqual(response.json()["merchant"]["id"], "zyrTds13x")
        self.assertEqual(response.json()["merchant"]["name"], "New Merchant")
        self.assertEqual(response.json()["merchant"]["description"], "New Description")
        self.assertEqual(response.json()["merchant"]["website"], "http://newmerchant.com")

        # Check OpenSearch client call
        self.os_client.index.assert_called_once_with(
            index="merchants",
            body={
                "name": "New Merchant",
                "description": "New Description",
                "website": "http://newmerchant.com",
                "created": datetime.datetime(2024, 12, 1, 21, 26, 53, 532000),
                "updated": datetime.datetime(2024, 12, 1, 21, 26, 53, 532000),
            },
        )

    def test_post_merchant_invalid_data(self) -> None:
        # Call our API
        response = self.rest_client.post(
            path=self.rest_endpoint,
            data=json.dumps(
                {
                    "name": "New Merchant",
                    # Missing description
                    "website": "http://newmerchant.com",
                }
            ),
            content_type="application/json",
        )

        # Check API response
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "Invalid data"})

        # OpenSearch is not called as data validation failed
        self.os_client.index.assert_not_called()
