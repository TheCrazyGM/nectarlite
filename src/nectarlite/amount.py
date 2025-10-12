"""Amount class for serializing Hive amounts."""

import struct

from .asset import Asset
from .types import Uint8

WIRE_SYMBOL_ALIASES = {
    "HIVE": "STEEM",
    "HBD": "SBD",
}


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
        wire_symbol = WIRE_SYMBOL_ALIASES.get(self.asset.symbol, self.asset.symbol)

        symbol_bytes = wire_symbol.encode("ascii")
        if len(symbol_bytes) > 7:
            raise ValueError("Asset symbol must be 7 characters or fewer")
        padded_symbol = symbol_bytes + b"\x00" * (7 - len(symbol_bytes))

        return (
            struct.pack("<q", amount)
            + bytes(Uint8(self.asset["precision"]))
            + padded_symbol
        )

    def __str__(self):
        """Return the amount as a string."""
        return f"{self.amount} {self.asset.symbol}"
