"""Unit tests for the Account class."""

import unittest
from unittest.mock import MagicMock

from nectarlite.account import Account


class TestAccount(unittest.TestCase):
    """Unit tests for the Account class."""

    def setUp(self):
        self.api = MagicMock()
        self.api.call.return_value = [
            {
                "name": "testaccount",
                "balance": "1.000 HIVE",
                "vesting_shares": "1000.000000 VESTS",
            }
        ]

    def test_initialization(self):
        """Test Account initialization."""
        account = Account("testaccount", api=self.api)
        self.assertEqual(account.name, "testaccount")

    def test_refresh(self):
        """Test the refresh method."""
        account = Account("testaccount", api=self.api)
        account.refresh()
        self.assertEqual(account["name"], "testaccount")
        self.assertEqual(account["balance"], "1.000 HIVE")

    def test_getitem(self):
        """Test the __getitem__ method."""
        account = Account("testaccount", api=self.api)
        account.refresh()
        self.assertEqual(account["balance"], "1.000 HIVE")

    def test_str(self):
        """Test the __str__ method."""
        account = Account("testaccount", api=self.api)
        self.assertEqual(str(account), "<Account testaccount>")


if __name__ == "__main__":
    unittest.main()
