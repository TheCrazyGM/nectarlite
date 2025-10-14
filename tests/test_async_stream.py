# -*- coding: utf-8 -*-
from unittest.mock import Mock

import pytest

from nectarlite.api import Api
from nectarlite.stream import AsyncStream


@pytest.fixture
def async_mock_api_factory():
    """Factory returning a mock Api suitable for async tests."""

    def factory():
        api = Mock(spec=Api)

        mock_blocks = {
            1: {
                "block_id": 1,
                "transactions": [
                    {"operations": [("transfer", {"sender": "a", "to": "b"})]}
                ],
            },
            2: {
                "block_id": 2,
                "transactions": [{"operations": [("vote", {"voter": "c"})]}],
            },
        }

        last_block = [1]

        def call_side_effect(api_name, method, params=None):
            params = params or []
            if method == "get_dynamic_global_properties":
                last_block[0] += 1
                return {"last_irreversible_block_num": last_block[0]}
            if method == "get_block":
                block_num = params[0]
                return mock_blocks.get(block_num)
            raise AssertionError(f"Unexpected method {method}")

        api.call.side_effect = call_side_effect
        return api

    return factory


@pytest.mark.asyncio
async def test_async_stream_blocks(async_mock_api_factory):
    mock_api = async_mock_api_factory()
    listener = AsyncStream(api=mock_api, start_block=1, end_block=2)

    collected = []
    async for block in listener.stream_blocks():
        collected.append(block)

    assert len(collected) == 2
    assert collected[0].data["block_id"] == 1


@pytest.mark.asyncio
async def test_async_stream_ops(async_mock_api_factory):
    mock_api = async_mock_api_factory()
    listener = AsyncStream(api=mock_api, start_block=1, end_block=2)

    collected = []
    async for op in listener.stream_ops():
        collected.append(op)

    assert len(collected) == 2
    assert collected[1].type == "vote"


@pytest.mark.asyncio
async def test_async_stream_on_filter(async_mock_api_factory):
    mock_api = async_mock_api_factory()
    listener = AsyncStream(api=mock_api, start_block=1, end_block=2)

    collected = []
    async for op in listener.on("transfer", filter_by={"to": "b"}):
        collected.append(op)

    assert len(collected) == 1
    assert collected[0].sender == "a"
