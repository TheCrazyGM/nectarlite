"""Tests for helper functions wrapping Hive read-only APIs."""

import unittest
from unittest.mock import MagicMock

from nectarlite.api import Api
from nectarlite.exceptions import NodeError
from nectarlite.helpers import (
    DynamicGlobalProperties,
    RewardFunds,
    get_account_history,
    get_block,
    get_market_ticker,
    get_ops_in_block,
    get_ranked_posts,
    get_rc_accounts,
)


class DummyApi(Api):
    def __init__(self):
        self.calls = []

    def call(self, api, method, params=None):
        self.calls.append((api, method, params))
        return MagicMock()


class TestHelpers(unittest.TestCase):
    def setUp(self):
        self.api = MagicMock(spec=Api)

    def test_lazy_resources_fetch_once(self):
        self.api.call.return_value = {"head_block_number": 123}
        dgp = DynamicGlobalProperties(self.api)
        self.assertEqual(dgp.head_block_number, 123)
        # Second access should use cached data
        self.assertEqual(dgp.head_block_number, 123)
        self.api.call.assert_called_once_with(
            "condenser_api", "get_dynamic_global_properties", []
        )

    def test_reward_funds_find(self):
        funds = {
            "funds": [
                {"name": "post", "reward_balance": "100.000 HIVE"},
                {"name": "comment", "reward_balance": "50.000 HIVE"},
            ]
        }
        self.api.call.return_value = funds
        rf = RewardFunds(self.api)
        self.assertEqual(rf.find("comment"), funds["funds"][1])
        self.assertIsNone(rf.find("nonexistent"))

    def test_reward_funds_fallback_condenser(self):
        def call_side_effect(api, method, params=None):
            if api == "database_api":
                raise NodeError("database api not available")
            if api == "condenser_api" and method == "get_reward_fund":
                return {"name": params[0], "reward_balance": "10.000 HIVE"}
            raise AssertionError("Unexpected call")

        self.api.call.side_effect = call_side_effect

        rf = RewardFunds(self.api)
        funds = rf.as_list()
        self.assertTrue(funds)
        self.assertIn(funds[0]["name"], RewardFunds._FALLBACK_FUNDS)

    def test_get_block(self):
        self.api.call.return_value = {"block": {"transactions": []}}
        block = get_block(self.api, 42)
        self.assertEqual(block, {"transactions": []})
        self.api.call.assert_called_with("block_api", "get_block", {"block_num": 42})

    def test_get_ops_in_block(self):
        self.api.call.return_value = [{"op": "vote"}]
        ops = get_ops_in_block(self.api, 123)
        self.assertEqual(ops, [{"op": "vote"}])

    def test_get_account_history(self):
        history = [[0, {"op": "vote"}]]
        self.api.call.return_value = history
        result = get_account_history(self.api, "alice")
        self.assertEqual(result, history)

    def test_get_rc_accounts(self):
        rc_info = {"rc_accounts": [{"account": "alice"}]}
        self.api.call.return_value = rc_info
        accounts = get_rc_accounts(self.api, ["alice"])
        self.assertEqual(accounts, rc_info["rc_accounts"])

    def test_get_market_ticker(self):
        ticker = {"latest": "0.500"}
        self.api.call.return_value = ticker
        self.assertEqual(get_market_ticker(self.api), ticker)

    def test_get_ranked_posts(self):
        posts = [{"author": "alice"}]
        self.api.call.return_value = posts
        result = get_ranked_posts(self.api, sort="created", tag="hive")
        self.assertEqual(result, posts)
        self.api.call.assert_called_with(
            "bridge",
            "get_ranked_posts",
            {"sort": "created", "limit": 20, "tag": "hive"},
        )


if __name__ == "__main__":
    unittest.main()
