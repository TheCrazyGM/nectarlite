#!/usr/bin/env python

from nectarlite.api import Api
from nectarlite.vote import Vote

# Initialize the API
nodes = ["https://api.hive.blog", "https://api.openhive.network"]
api = Api(nodes)

# Get a vote
vote = Vote(voter="testvoter", author="testauthor", permlink="test-permlink", api=api)

# The vote data is automatically fetched when you access an attribute
print(f"Voter: {vote.voter}")
print(f"Author: {vote.author}")
print(f"Permlink: {vote.permlink}")
print(f"Weight: {vote.weight}")
