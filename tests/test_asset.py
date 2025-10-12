"""Unit tests for the Asset class."""

import unittest
from unittest.mock import MagicMock

from nectarlite.asset import Asset


class TestAsset(unittest.TestCase):
    """Unit tests for the Asset class."""

    def setUp(self):
        self.api = MagicMock()
        self.api.call.return_value = [
            {
                "symbol": "HIVE",
                "precision": 3,
            }
        ]

    def test_initialization(self):
        """Test Asset initialization."""
        asset = Asset("HIVE", api=self.api)
        self.assertEqual(asset.symbol, "HIVE")

    def test_refresh(self):
        """Test the refresh method."""
        asset = Asset("HIVE", api=self.api)
        asset.refresh()
        self.assertEqual(asset["symbol"], "HIVE")
        self.assertEqual(asset["precision"], 3)

    def test_getitem(self):
        """Test the __getitem__ method."""
        asset = Asset("HIVE", api=self.api)
        asset.refresh()
        self.assertEqual(asset["symbol"], "HIVE")

    def test_str(self):
        """Test the __str__ method."""
        asset = Asset("HIVE", api=self.api)
        self.assertEqual(str(asset), "<Asset HIVE>")


if __name__ == "__main__":
    unittest.main()
