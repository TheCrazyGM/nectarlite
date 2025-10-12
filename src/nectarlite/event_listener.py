# -*- coding: utf-8 -*-
import logging
import time

log = logging.getLogger(__name__)


class BlockListener:
    """The base class for listening to the blockchain for new blocks."""

    def __init__(
        self, api, blockchain_mode="irreversible", start_block=None, end_block=None
    ):
        self.api = api
        self.blockchain_mode = blockchain_mode
        self.start_block = start_block
        self.end_block = end_block

    def get_last_block_height(self):
        """Get the last block height based on the chosen blockchain mode."""
        props = self.api.call("condenser_api", "get_dynamic_global_properties")
        if self.blockchain_mode == "irreversible":
            return props["last_irreversible_block_num"]
        elif self.blockchain_mode == "head":
            return props["head_block_number"]
        else:
            raise ValueError(
                "Invalid blockchain mode. Must be 'irreversible' or 'head'."
            )

    def stream_blocks(self):
        """Yields full blocks from the blockchain."""
        current_block = self.start_block
        if not current_block:
            current_block = self.get_last_block_height()

        while True:
            while (self.get_last_block_height() - current_block) > 0:
                if self.end_block and current_block > self.end_block:
                    return

                log.debug(f"Getting block: {current_block}")
                block_data = self.api.call(
                    "condenser_api", "get_block", [current_block]
                )
                if block_data:
                    yield block_data

                current_block += 1

            log.debug("Waiting for new blocks...")
            time.sleep(3)


class EventListener:
    """Listen for specific events on the Hive blockchain."""

    def __init__(
        self, api, blockchain_mode="irreversible", start_block=None, end_block=None
    ):
        self.api = api
        self.block_listener = BlockListener(
            self.api,
            blockchain_mode=blockchain_mode,
            start_block=start_block,
            end_block=end_block,
        )

    def stream_ops(self):
        """Yields all operations from the blockchain."""
        for block in self.block_listener.stream_blocks():
            if "transactions" not in block:
                continue
            for trx in block["transactions"]:
                for op in trx["operations"]:
                    yield {
                        "block_num": block["block_id"],
                        "op": op,
                    }

    def on(self, op_type, filter_by=None, condition=None):
        """Listen for a specific operation type."""
        op_types = op_type if isinstance(op_type, list) else [op_type]

        for op_data in self.stream_ops():
            operation_type, operation_value = op_data["op"]
            if operation_type not in op_types:
                continue

            if filter_by and not filter_by.items() <= operation_value.items():
                continue

            if condition and not condition(operation_value):
                continue

            yield op_data

    def stream_blocks(self):
        """Yields all blocks from the blockchain."""
        for block in self.block_listener.stream_blocks():
            yield block
