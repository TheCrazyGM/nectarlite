"""Amount class for serializing Hive amounts."""

import struct

from .asset import Asset
from .types import String, Uint8


class Amount:
    """Amount class for serializing Hive amounts."""

    def __init__(self, amount, asset, api=None):
        """Initialize the Amount class.

        :param float amount: The amount.
        :param str asset: The asset symbol.
        :param Api api: An instance of the Api class.
        """
        self.amount = float(amount)
        if isinstance(asset, str):
            self.asset = Asset(asset, api=api)
        else:
            self.asset = asset

    def __bytes__(self):
        """Return the binary representation of the amount."""
        # refresh asset if necessary
        if not self.asset["precision"]:
            self.asset.refresh()
        amount = int(self.amount * (10 ** self.asset["precision"]))
        return (
            struct.pack("<q", amount)
            + bytes(Uint8(self.asset["precision"]))
            + bytes(String(self.asset.symbol))
        )

    def __str__(self):
        """Return the amount as a string."""
        return f"{self.amount} {self.asset.symbol}"
