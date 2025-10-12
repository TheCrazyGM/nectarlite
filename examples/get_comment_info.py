#!/usr/bin/env python

from nectarlite.api import Api
from nectarlite.comment import Comment

# Initialize the API
nodes = ["https://api.hive.blog", "https://api.openhive.network"]
api = Api(nodes)

# Get a comment
comment = Comment(author="testauthor", permlink="test-permlink", api=api)

# The comment data is automatically fetched when you access an attribute
print(f"Title: {comment.title}")
print(f"Author: {comment.author}")
print(f"Permlink: {comment.permlink}")
print(f"Pending Payout: {comment.pending_payout_value}")
