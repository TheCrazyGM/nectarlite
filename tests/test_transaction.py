"""Unit tests for the Transaction class."""

import unittest
from unittest.mock import MagicMock, patch

from nectarlite.exceptions import TransactionError
from nectarlite.transaction import Transaction, Transfer


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


if __name__ == "__main__":
    unittest.main()
