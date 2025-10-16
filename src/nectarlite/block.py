"""Block class for interacting with Hive blocks."""

import logging

from .exceptions import NodeError

log = logging.getLogger(__name__)


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
            log.error("Cannot refresh block %s: API not configured.", self.block_num)
            raise ValueError("API not configured.")
        log.debug("Requesting block %s.", self.block_num)
        try:
            self._data = self.api.call("condenser_api", "get_block", [self.block_num])
        except Exception as exc:  # noqa: BLE001 - surface as NodeError
            if isinstance(exc, NodeError):
                raise
            log.error("Error retrieving block %s: %s", self.block_num, exc)
            raise NodeError(str(exc)) from exc

    @property
    def data(self):
        return self._data

    def __getitem__(self, key):
        return self._data.get(key)

    def __str__(self):
        return f"<Block {self.block_num}>"
