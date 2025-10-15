# -*- coding: utf-8 -*-
import asyncio
import logging
import time

from .block import Block
from .exceptions import NodeError

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
        try:
            props = self.api.call("condenser_api", "get_dynamic_global_properties")
        except Exception as exc:  # noqa: BLE001 - surface as NodeError
            if isinstance(exc, NodeError):
                raise
            raise NodeError(str(exc)) from exc
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
            while True:
                try:
                    current_block = self.get_last_block_height()
                    break
                except NodeError as exc:
                    log.warning("Unable to determine starting block: %s", exc)
                    time.sleep(3)

        while True:
            try:
                while (self.get_last_block_height() - current_block) > 0:
                    if self.end_block and current_block > self.end_block:
                        return

                    log.debug(f"Getting block: {current_block}")
                    try:
                        block_data = self.api.call(
                            "condenser_api", "get_block", [current_block]
                        )
                    except Exception as exc:  # noqa: BLE001 - surface as NodeError
                        if isinstance(exc, NodeError):
                            raise
                        raise NodeError(str(exc)) from exc
                    if block_data:
                        yield Block(
                            current_block,
                            api=self.api,
                            data=block_data,
                        )

                    current_block += 1
            except NodeError as exc:
                log.warning("Node error while streaming blocks: %s", exc)
                time.sleep(3)
                continue

            log.debug("Waiting for new blocks...")
            time.sleep(3)


class Op:
    """Represents an operation within a block."""

    def __init__(
        self,
        block,
        op_type,
        op_value,
        transaction=None,
        transaction_index=None,
        op_index=None,
    ):
        self.block = block
        self.type = op_type
        self.value = op_value
        self.transaction = transaction
        self.transaction_index = transaction_index
        self.op_index = op_index

    @property
    def block_num(self):
        return self.block.block_num

    @property
    def block_id(self):
        return self.block.data.get("block_id")

    @property
    def op(self):
        return (self.type, self.value)

    def __getitem__(self, key):
        if key == "op":
            return self.op
        if key == "block_num":
            return self.block_num
        if key == "block_id":
            return self.block_id
        if key == "transaction":
            return self.transaction
        if key == "transaction_index":
            return self.transaction_index
        if key == "op_index":
            return self.op_index
        return self.value[key]

    def get(self, key, default=None):
        try:
            return self[key]
        except (KeyError, AttributeError):
            return default

    def __contains__(self, key):
        try:
            self[key]
        except (KeyError, AttributeError):
            return False
        return True

    def __getattr__(self, item):
        if item in self.__dict__ or item in {"type", "value"}:
            return self.__dict__[item]
        if isinstance(self.value, dict) and item in self.value:
            return self.value[item]
        raise AttributeError(item)

    def __repr__(self):
        return f"<Op type={self.type} block={self.block_num}>"


class Stream:
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
            transactions = block["transactions"]
            if not transactions:
                continue
            for trx_idx, trx in enumerate(transactions):
                for op_idx, op in enumerate(trx["operations"]):
                    op_type, op_value = op
                    yield Op(
                        block,
                        op_type,
                        op_value,
                        transaction=trx,
                        transaction_index=trx_idx,
                        op_index=op_idx,
                    )

    def on(self, op_type, filter_by=None, condition=None):
        """Listen for a specific operation type."""
        op_types = op_type if isinstance(op_type, list) else [op_type]

        for op_data in self.stream_ops():
            if op_data.type not in op_types:
                continue

            if filter_by and not filter_by.items() <= op_data.value.items():
                continue

            if condition and not condition(op_data.value):
                continue

            yield op_data

    def stream_blocks(self):
        """Yields all blocks from the blockchain."""
        for block in self.block_listener.stream_blocks():
            yield block


class AsyncBlockListener:
    """Async variant of :class:`BlockListener` using asyncio-friendly calls."""

    def __init__(
        self, api, blockchain_mode="irreversible", start_block=None, end_block=None
    ):
        self.api = api
        self.blockchain_mode = blockchain_mode
        self.start_block = start_block
        self.end_block = end_block

    async def _call(self, api_name, method, params=None):
        params = params or []
        try:
            return await asyncio.to_thread(self.api.call, api_name, method, params)
        except Exception as exc:  # noqa: BLE001 - surface as NodeError
            if isinstance(exc, NodeError):
                raise
            raise NodeError(str(exc)) from exc

    async def get_last_block_height(self):
        props = await self._call("condenser_api", "get_dynamic_global_properties", [])
        if self.blockchain_mode == "irreversible":
            return props["last_irreversible_block_num"]
        elif self.blockchain_mode == "head":
            return props["head_block_number"]
        else:
            raise ValueError(
                "Invalid blockchain mode. Must be 'irreversible' or 'head'."
            )

    async def stream_blocks(self):
        """Asynchronously yield full blocks from the blockchain."""

        current_block = self.start_block
        if not current_block:
            while True:
                try:
                    current_block = await self.get_last_block_height()
                    break
                except NodeError as exc:
                    log.warning("Unable to determine starting block: %s", exc)
                    await asyncio.sleep(3)

        while True:
            try:
                while (await self.get_last_block_height() - current_block) > 0:
                    if self.end_block and current_block > self.end_block:
                        return

                    log.debug(f"Getting block: {current_block}")
                    block_data = await self._call(
                        "condenser_api", "get_block", [current_block]
                    )
                    if block_data:
                        yield Block(
                            current_block,
                            api=self.api,
                            data=block_data,
                        )

                    current_block += 1
            except NodeError as exc:
                log.warning("Node error while streaming blocks: %s", exc)
                await asyncio.sleep(3)
                continue

            log.debug("Waiting for new blocks...")
            await asyncio.sleep(3)


class AsyncStream:
    """Async listener mirroring :class:`Stream` semantics with asyncio support."""

    def __init__(
        self, api, blockchain_mode="irreversible", start_block=None, end_block=None
    ):
        self.api = api
        self.block_listener = AsyncBlockListener(
            self.api,
            blockchain_mode=blockchain_mode,
            start_block=start_block,
            end_block=end_block,
        )

    async def stream_ops(self):
        """Asynchronously yield all operations from the blockchain."""

        async for block in self.block_listener.stream_blocks():
            transactions = block["transactions"]
            if not transactions:
                continue
            for trx_idx, trx in enumerate(transactions):
                for op_idx, op in enumerate(trx["operations"]):
                    op_type, op_value = op
                    yield Op(
                        block,
                        op_type,
                        op_value,
                        transaction=trx,
                        transaction_index=trx_idx,
                        op_index=op_idx,
                    )

    async def on(self, op_type, filter_by=None, condition=None):
        """Asynchronously listen for a specific operation type."""

        op_types = op_type if isinstance(op_type, list) else [op_type]

        async for op_data in self.stream_ops():
            if op_data.type not in op_types:
                continue

            if filter_by and not filter_by.items() <= op_data.value.items():
                continue

            if condition and not condition(op_data.value):
                continue

            yield op_data

    async def stream_blocks(self):
        """Asynchronously yield all blocks from the blockchain."""

        async for block in self.block_listener.stream_blocks():
            yield block
