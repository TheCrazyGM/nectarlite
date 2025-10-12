# -*- coding: utf-8 -*-
from unittest.mock import Mock

import pytest

from nectarlite.api import Api
from nectarlite.stream import Stream


@pytest.fixture
def mock_api_factory():
    """A factory to create a new, stateful mock_api for each test."""

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
            3: {
                "block_id": 3,
                "transactions": [
                    {"operations": [("transfer", {"sender": "f", "to": "g"})]}
                ],
            },
            4: {"block_id": 4, "transactions": []},
        }

        # Use a list as a simple, mutable state container for the block height
        last_block = [1]

        def call_side_effect(api_name, method, params=[]):
            if method == "get_block":
                return mock_blocks.get(params[0])
            if method == "get_dynamic_global_properties":
                last_block[0] += 1
                return {"last_irreversible_block_num": last_block[0]}
            return {}

        api.call.side_effect = call_side_effect
        return api

    return factory


def test_stream_blocks(mock_api_factory):
    """Tests that the listener correctly streams a range of blocks."""
    mock_api = mock_api_factory()  # Get a fresh mock
    listener = Stream(api=mock_api, start_block=1, end_block=3)
    blocks = list(listener.stream_blocks())
    assert len(blocks) == 3
    assert blocks[2]["block_id"] == 3


def test_stream_ops(mock_api_factory):
    """Tests that the listener correctly extracts all operations from blocks."""
    mock_api = mock_api_factory()  # Get a fresh mock
    listener = Stream(api=mock_api, start_block=1, end_block=3)
    ops = list(listener.stream_ops())
    assert len(ops) == 3
    assert ops[1]["op"][0] == "vote"


def test_on_filter_by_content(mock_api_factory):
    """Tests filtering operations by their content."""
    mock_api = mock_api_factory()  # Get a fresh mock
    listener = Stream(api=mock_api, start_block=1, end_block=3)
    filtered_ops = list(listener.on("transfer", filter_by={"to": "g"}))
    assert len(filtered_ops) == 1
    assert filtered_ops[0]["op"][1]["sender"] == "f"


def test_on_filter_by_op_type(mock_api_factory):
    """Tests filtering operations by just their type."""
    mock_api = mock_api_factory()  # Get a fresh mock
    listener = Stream(api=mock_api, start_block=1, end_block=3)
    transfer_ops = list(listener.on("transfer"))
    assert len(transfer_ops) == 2
