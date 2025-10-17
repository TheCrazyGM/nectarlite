"""Unit tests for the Api class."""

import unittest
from unittest.mock import MagicMock, patch

import httpx

from nectarlite.api import Api


class TestApi(unittest.TestCase):
    """Unit tests for the Api class."""

    def setUp(self):
        self.nodes = ["https://api.hive.blog", "https://api.syncad.com"]
        self.api = Api(self.nodes)

    @patch("httpx.Client.post")
    def test_successful_call(self, mock_post):
        """Test a successful API call."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": "success"}
        mock_post.return_value = mock_response

        result = self.api.call("condenser_api", "get_block", [1])
        self.assertEqual(result, "success")

    @patch("httpx.Client.post")
    def test_failed_call(self, mock_post):
        """Test a failed API call."""
        mock_response_success = MagicMock()
        mock_response_success.status_code = 200
        mock_response_success.json.return_value = {"result": "success"}

        mock_post.side_effect = [
            httpx.HTTPError("Connection error"),
            mock_response_success,
        ]

        result = self.api.call("condenser_api", "get_block", [1])
        self.assertEqual(result, "success")

    @patch("httpx.Client.post")
    def test_call_with_mapping_params(self, mock_post):
        """Ensure dict parameters are passed through unmodified."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": {"block": {}}}
        mock_post.return_value = mock_response

        params = {"block_num": 42}
        result = self.api.call("block_api", "get_block", params)

        self.assertEqual(result, {"block": {}})
        mock_post.assert_called_once()
        posted_payload = mock_post.call_args.kwargs["json"]
        self.assertEqual(posted_payload["params"], params)


if __name__ == "__main__":
    unittest.main()
