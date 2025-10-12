#!/usr/bin/env python

from nectarlite.account import Account
from nectarlite.api import Api

# Initialize the API
nodes = ["https://api.hive.blog", "https://api.openhive.network"]
api = Api(nodes)

# Get an account
account = Account("thecrazygm", api=api)

# The account data is automatically fetched when you access an attribute
print(f"Account Name: {account.name}")
print(f"Balance: {account.balance}")
print(f"Vesting Shares: {account.vesting_shares}")
