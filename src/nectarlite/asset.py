"""Asset class for interacting with Hive assets."""


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

    def refresh(self):
        """Fetch the asset data from the blockchain."""
        if not self.api:
            raise ValueError("API not configured.")
        result = self.api.call("condenser_api", "lookup_asset_symbols", [[self.symbol]])
        if result:
            self._data = result[0]

    def __getitem__(self, key):
        return self._data.get(key)

    def __str__(self):
        return f"<Asset {self.symbol}>"
