"""Unit tests for the Transaction class."""

import json
import unittest
from unittest.mock import MagicMock, patch

from nectarlite.exceptions import TransactionError
from nectarlite.transaction import (
    CommentOperation,
    CommentOptionsOperation,
    Follow,
    Transaction,
    Transfer,
)


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
                "head_block_id": "0000303901020304000000000000000000000000000000000000000000000000",
                "time": "2024-01-01T00:00:00",
            }
        elif method == "get_block":
            return {
                "block": {
                    "previous": "0000303801020304000000000000000000000000000000000000000000000000"
                }
            }
        elif method == "get_transaction_hex":
            return "deadbeef"
        elif method == "broadcast_transaction_synchronous":
            return {"id": "123"}

    def test_set_block_params(self):
        """Test the _set_block_params method."""
        self.tx._set_block_params()
        self.assertEqual(self.tx.ref_block_num, 12342)
        self.assertEqual(self.tx.ref_block_prefix, 0x04030201)

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
                "head_block_id": "0000303901020304000000000000000000000000000000000000000000000000",
                "time": "2024-01-01T00:00:00",
            }
        elif method == "get_block":
            return {
                "block": {
                    "previous": "0000303801020304000000000000000000000000000000000000000000000000"
                }
            }
        elif method == "get_transaction_hex":
            return "deadbeef"
        elif method == "broadcast_transaction_synchronous":
            raise TransactionError("Broadcast failed")

    @patch("nectarlite.transaction.sign")
    def test_transfer_wire_format(self, mock_sign):
        """Ensure transfer serialization uses canonical amount string and legacy wire symbol."""

        mock_signature = bytes([31]) + b"\x00" * 64
        mock_sign.return_value = mock_signature

        self.tx.append_op(Transfer(to="test", amount="1.000", asset="HIVE", frm="test"))
        self.tx.sign("5J...")

        tx_dict = self.tx._construct_tx()
        self.assertEqual(tx_dict["operations"][0][1]["amount"], "1.000 HIVE")

        serialized = self.tx._serialize_tx()
        self.assertIn(b"STEEM", serialized)

    @patch("nectarlite.transaction.sign")
    def test_comment_with_options_bundle(self, mock_sign):
        """Ensure comment and comment_options operations can be bundled in one transaction."""

        mock_signature = bytes([42]) + b"\x01" * 64
        mock_sign.return_value = mock_signature

        comment = CommentOperation(
            parent_author="",
            parent_permlink="hive-12345",
            author="alice",
            permlink="hello-hive",
            title="Hello Hive",
            body="This is a sample post body.",
            json_metadata='{"tags": ["hive", "nectarlite"]}',
        )
        options = CommentOptionsOperation(
            author="alice",
            permlink="hello-hive",
            max_accepted_payout="1000.000 HBD",
            percent_steem_dollars=10000,
            allow_votes=True,
            allow_curation_rewards=True,
        )

        self.tx.append_op(comment)
        self.tx.append_op(options)

        self.tx.sign("5J...")

        tx_dict = self.tx._construct_tx()
        operations = tx_dict["operations"]

        self.assertEqual(len(operations), 2)
        self.assertEqual(operations[0][0], "comment")
        self.assertEqual(operations[1][0], "comment_options")
        self.assertEqual(operations[0][1]["author"], "alice")
        self.assertEqual(operations[1][1]["max_accepted_payout"], "1000.000 HBD")


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
        self.assertEqual(
            follow_op.custom_json.params["required_posting_auths"], [follower]
        )

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
