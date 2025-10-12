#!/usr/bin/env python

from nectarlite.account import Account
from nectarlite.api import Api
from nectarlite.comment import Comment

# Initialize the API
nodes = ["https://api.hive.blog", "https://api.syncad.com"]
api = Api(nodes)

# Get a real comment from the blockchain by fetching the latest post from a known account
print("Fetching the latest post from @gtg to use as a real-world example...")
try:
    # Using the Account class to get recent posts
    account = Account("gtg", api=api)
    # The condenser_api call for get_discussions_by_blog is a bit complex, let's use a direct call
    latest_post = api.call(
        "condenser_api", "get_discussions_by_blog", [{"tag": "gtg", "limit": 1}]
    )[0]

    author = latest_post["author"]
    permlink = latest_post["permlink"]

    print(f"Found post: @{author}/{permlink}\n")

    # Get the comment
    comment = Comment(author=author, permlink=permlink, api=api)

    # The comment data is automatically fetched when you access an attribute
    print(f"Title: {comment.title}")
    print(f"Author: {comment.author}")
    print(f"Permlink: {comment.permlink}")
    print(f"Pending Payout: {comment.pending_payout_value}")

except Exception as e:
    print(f"An error occurred: {e}")
    print(
        "This might be due to a temporary API issue or if the @gtg account has no posts."
    )
