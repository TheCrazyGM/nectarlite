"""Unit tests for the Block class."""

import unittest
from unittest.mock import MagicMock

from nectarlite.block import Block


class TestBlock(unittest.TestCase):
    """Unit tests for the Block class."""

    def setUp(self):
        self.api = MagicMock()
        self.api.call.return_value = {
            "previous": "0000000000000000000000000000000000000000",
            "timestamp": "2023-10-27T10:00:00",
            "transactions": [],
        }

    def test_initialization(self):
        """Test Block initialization."""
        block = Block(1, api=self.api)
        self.assertEqual(block.block_num, 1)

    def test_refresh(self):
        """Test the refresh method."""
        block = Block(1, api=self.api)
        block.refresh()
        self.assertEqual(block["timestamp"], "2023-10-27T10:00:00")

    def test_getitem(self):
        """Test the __getitem__ method."""
        block = Block(1, api=self.api)
        block.refresh()
        self.assertEqual(block["transactions"], [])

    def test_str(self):
        """Test the __str__ method."""
        block = Block(1, api=self.api)
        self.assertEqual(str(block), "<Block 1>")


if __name__ == "__main__":
    unittest.main()
