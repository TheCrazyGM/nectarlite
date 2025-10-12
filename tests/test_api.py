"""Unit tests for the Api class."""

import unittest
from unittest.mock import MagicMock, patch

import requests

from nectarlite.api import Api


class TestApi(unittest.TestCase):
    """Unit tests for the Api class."""

    def setUp(self):
        self.nodes = ["https://api.hive.blog", "https://api.syncad.com"]
        self.api = Api(self.nodes)

    @patch("requests.post")
    def test_successful_call(self, mock_post):
        """Test a successful API call."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": "success"}
        mock_post.return_value = mock_response

        result = self.api.call("condenser_api", "get_block", [1])
        self.assertEqual(result, "success")

    @patch("requests.post")
    def test_failed_call(self, mock_post):
        """Test a failed API call."""
        mock_response_success = MagicMock()
        mock_response_success.status_code = 200
        mock_response_success.json.return_value = {"result": "success"}

        mock_post.side_effect = [
            requests.exceptions.RequestException("Connection error"),
            mock_response_success,
        ]

        result = self.api.call("condenser_api", "get_block", [1])
        self.assertEqual(result, "success")


if __name__ == "__main__":
    unittest.main()
