"""Block class for interacting with Hive blocks."""

from .exceptions import NodeError


class Block:
    """Block class for interacting with Hive blocks."""

    def __init__(self, block_num, api=None, data=None):
        """Initialize the Block class.

        :param int block_num: The block number.
        :param Api api: An instance of the Api class.
        """
        self.block_num = block_num
        self.api = api
        self._data = data or {}

    def refresh(self):
        """Fetch the block data from the blockchain."""
        if not self.api:
            raise ValueError("API not configured.")
        try:
            self._data = self.api.call("condenser_api", "get_block", [self.block_num])
        except Exception as exc:  # noqa: BLE001 - surface as NodeError
            if isinstance(exc, NodeError):
                raise
            raise NodeError(str(exc)) from exc

    @property
    def data(self):
        return self._data

    def __getitem__(self, key):
        return self._data.get(key)

    def __str__(self):
        return f"<Block {self.block_num}>"
