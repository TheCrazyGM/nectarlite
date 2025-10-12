"""Unit tests for the Amount class."""

import struct
import unittest
from unittest.mock import MagicMock

from nectarlite.amount import Amount
from nectarlite.types import Uint8


class TestAmount(unittest.TestCase):
    """Unit tests for the Amount class."""

    def setUp(self):
        self.api = MagicMock()
        self.api.call.return_value = [
            {
                "symbol": "HIVE",
                "precision": 3,
            }
        ]

    def test_initialization(self):
        """Test Amount initialization."""
        amount = Amount(1.000, "HIVE", api=self.api)
        self.assertEqual(amount.amount, 1.000)
        self.assertEqual(amount.asset.symbol, "HIVE")

    def test_bytes(self):
        """Test the __bytes__ method."""
        amount = Amount(1.000, "HIVE", api=self.api)
        expected_bytes = (
            struct.pack("<q", 1000) + bytes(Uint8(3)) + b"STEEM\x00\x00"
        )
        self.assertEqual(bytes(amount), expected_bytes)

    def test_str(self):
        """Test the __str__ method."""
        amount = Amount(1.000, "HIVE", api=self.api)
        self.assertEqual(str(amount), "1.0 HIVE")


if __name__ == "__main__":
    unittest.main()
