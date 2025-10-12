"""Example demonstrating helper utilities for Hive read-only APIs."""

import os

from nectarlite import Api
from nectarlite.helpers import (
    DynamicGlobalProperties,
    FeedHistory,
    RewardFunds,
    get_account_history,
    get_block,
    get_market_ticker,
    get_ops_in_block,
    get_ranked_posts,
)


def main():
    nodes = os.environ.get(
        "HIVE_NODES",
        "https://api.hive.blog,https://api.syncad.com",
    ).split(",")
    api = Api(nodes)

    # Lazy resources expose properties once fetched
    dgp = DynamicGlobalProperties(api)
    print("Head block number:", dgp.head_block_number)

    feed = FeedHistory(api)
    feed_data = feed.as_dict()
    median = feed_data.get("current_median_history", {})
    print(
        "Current median price:",
        f"{median.get('base')} / {median.get('quote')}" if median else "unavailable",
    )

    reward_funds = RewardFunds(api)
    funds = reward_funds.as_list()
    if funds:
        for fund in funds:
            name = fund.get("name", "unknown")
            balance = fund.get("reward_balance")
            print("Reward fund:", name, balance)
    else:
        print("Reward funds unavailable on current node")

    # Helper functions for direct responses
    block = get_block(api, dgp.head_block_number)
    if block:
        print(
            "Fetched block contains", len(block.get("transactions", [])), "transactions"
        )

    ops = get_ops_in_block(api, dgp.head_block_number, virtual_only=True)
    print("Virtual ops in head block:", len(ops))

    history = get_account_history(api, "hiveio", start=-1, limit=5)
    print("Recent account history entries:", len(history))

    ticker = get_market_ticker(api)
    if ticker:
        print("Market ticker latest price:", ticker.get("latest"))
    else:
        print("Ticker unavailable from current node")

    posts = get_ranked_posts(api, sort="trending", tag="hive", limit=3)
    for post in posts:
        print("Post:", post.get("author"), post.get("permlink"))


if __name__ == "__main__":
    main()
