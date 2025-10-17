#!/usr/bin/env python

from nectarlite.account import Account
from nectarlite import Api
from nectarlite.vote import CommentVote

# Initialize the API
nodes = ["https://api.hive.blog", "https://api.syncad.com"]
api = Api(nodes)

# Get a real vote from the blockchain by fetching a recent post and its voters
print("Fetching a real post and its voters to use as a real-world example...")
try:
    # Get a recent post from a well-known account
    account = Account("gtg", api=api)
    latest_post = api.call(
        "condenser_api", "get_discussions_by_blog", [{"tag": "gtg", "limit": 1}]
    )[0]
    author = latest_post["author"]
    permlink = latest_post["permlink"]

    # Get the active votes on that post
    active_votes = api.call("condenser_api", "get_active_votes", [author, permlink])

    if not active_votes:
        print("The latest post from @gtg has no active votes.")
    else:
        # Get the first voter from the list
        voter_info = active_votes[0]
        voter_name = voter_info["voter"]

        print(f"Found vote from {voter_name} on @{author}/{permlink}\n")

        # Get the vote
        vote = CommentVote(
            voter="aggroed",
            author="someauthor",
            permlink="some-permlink",
            api=api,
        )

        # The vote data is automatically fetched when you access an attribute
        print(f"Voter: {vote.voter}")
        print(f"Author: {vote.author}")
        print(f"Permlink: {vote.permlink}")

except Exception as e:
    print(f"An error occurred: {e}")
    print(
        "This might be due to a temporary API issue or if the @gtg account has no posts."
    )
