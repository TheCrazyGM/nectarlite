"""Asset class for interacting with Hive assets."""

DEFAULT_ASSETS = {
    "HIVE": {"symbol": "HIVE", "asset": "HIVE", "precision": 3, "id": 1},
    "HBD": {"symbol": "HBD", "asset": "HBD", "precision": 3, "id": 0},
    "VESTS": {"symbol": "VESTS", "asset": "VESTS", "precision": 6, "id": 2},
}

ASSET_ALIASES = {
    "STEEM": "HIVE",
    "SBD": "HBD",
    "VEST": "VESTS",
}


class Asset:
    """Asset class for interacting with Hive assets."""

    def __init__(self, asset_symbol, api=None):
        """Initialize the Asset class.

        :param str asset_symbol: The asset symbol.
        :param Api api: An instance of the Api class.
        """
        self.symbol = asset_symbol
        self.api = api
        self._data = {}
        self.refresh()

    def refresh(self):
        """Fetch the asset data from the blockchain."""
        symbol = self.symbol.upper()
        canonical = ASSET_ALIASES.get(symbol, symbol)
        asset_data = DEFAULT_ASSETS.get(canonical)

        if not asset_data:
            raise ValueError(f"Asset metadata not available for symbol '{self.symbol}'")

        self.symbol = canonical
        self._data = {
            "symbol": canonical,
            "asset": asset_data.get("asset", canonical),
            "precision": asset_data.get("precision", 3),
            "id": asset_data.get("id"),
        }

    def __getitem__(self, key):
        return self._data.get(key)

    def __str__(self):
        return f"<Asset {self.symbol}>"
