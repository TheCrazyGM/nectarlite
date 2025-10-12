"""Unit tests for the Transaction class."""

import json
import unittest
from unittest.mock import MagicMock, patch

from nectarlite.exceptions import TransactionError
from nectarlite.transaction import Follow, Transaction, Transfer


class TestTransaction(unittest.TestCase):
    """Unit tests for the Transaction class."""

    def setUp(self):
        self.api = MagicMock()
        self.tx = Transaction(api=self.api)
        self.api.call.side_effect = self.api_call_side_effect

    def api_call_side_effect(self, api, method, params):
        if method == "get_dynamic_global_properties":
            return {
                "head_block_number": 12345,
                "head_block_id": "0000303900000000000000000000000000000000",
            }
        elif method == "lookup_asset_symbols":
            return [
                {
                    "symbol": "HIVE",
                    "precision": 3,
                }
            ]
        elif method == "broadcast_transaction":
            return {"result": {"id": "123"}}

    def test_set_block_params(self):
        """Test the _set_block_params method."""
        self.tx._set_block_params()
        self.assertEqual(self.tx.ref_block_num, 12345)
        self.assertEqual(self.tx.ref_block_prefix, 12345)

    @patch("nectarlite.transaction.sign")
    def test_successful_broadcast(self, mock_sign):
        """Test a successful transaction broadcast."""
        self.tx.append_op(Transfer(to="test", amount="1.000", asset="HIVE", frm="test"))
        self.tx.sign("5J...")
        result = self.tx.broadcast()

        self.assertEqual(result, {"id": "123"})

    @patch("nectarlite.transaction.sign")
    def test_failed_broadcast(self, mock_sign):
        """Test a failed transaction broadcast."""
        mock_sign.return_value = b"signature"
        self.api.call.side_effect = self.api_call_side_effect_failed

        self.tx.append_op(Transfer(to="test", amount="1.000", asset="HIVE", frm="test"))
        self.tx.sign("5J...")

        with self.assertRaises(TransactionError):
            self.tx.broadcast()

    def api_call_side_effect_failed(self, api, method, params):
        if method == "get_dynamic_global_properties":
            return {
                "head_block_number": 12345,
                "head_block_id": "0000303900000000000000000000000000000000",
            }
        elif method == "lookup_asset_symbols":
            return [
                {
                    "symbol": "HIVE",
                    "precision": 3,
                }
            ]
        elif method == "broadcast_transaction":
            raise TransactionError("Broadcast failed")


class TestFollowOperation(unittest.TestCase):
    """Unit tests for the Follow operation."""

    def setUp(self):
        self.api = MagicMock()
        self.tx = Transaction(api=self.api)

    def test_follow_operation(self):
        """Test creating a follow operation."""
        follower = "alice"
        following = "bob"
        what = ["blog"]
        
        follow_op = Follow(follower, following, what)
        
        # Check that the operation type is custom_json
        self.assertEqual(follow_op.custom_json.op_name, "custom_json")
        
        # Check that the ID is 'follow'
        self.assertEqual(follow_op.custom_json.params["id"], "follow")
        
        # Check that posting auth is set correctly
        self.assertEqual(follow_op.custom_json.params["required_posting_auths"], [follower])
        
        # Parse and check the JSON payload
        json_data = json.loads(follow_op.custom_json.params["json"])
        self.assertEqual(json_data[0], "follow")
        self.assertEqual(json_data[1]["follower"], follower)
        self.assertEqual(json_data[1]["following"], following)
        self.assertEqual(json_data[1]["what"], what)

    def test_unfollow_operation(self):
        """Test creating an unfollow operation."""
        follower = "alice"
        following = "bob"
        what = []  # Empty list means unfollow
        
        unfollow_op = Follow(follower, following, what)
        
        json_data = json.loads(unfollow_op.custom_json.params["json"])
        self.assertEqual(json_data[1]["what"], [])

    def test_ignore_operation(self):
        """Test creating an ignore operation."""
        follower = "alice"
        following = "bob"
        what = ["ignore"]  # 'ignore' means mute
        
        ignore_op = Follow(follower, following, what)
        
        json_data = json.loads(ignore_op.custom_json.params["json"])
        self.assertEqual(json_data[1]["what"], ["ignore"])


if __name__ == "__main__":
    unittest.main()
