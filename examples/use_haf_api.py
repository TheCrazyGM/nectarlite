#!/usr/bin/env python

from nectarlite.haf import HAF

# Initialize the HAF client
haf = HAF()

# Get an account's reputation
reputation = haf.reputation("thecrazygm")
print(f"Reputation for thecrazygm: {reputation['reputation']}")

# Get an account's balances
balances = haf.get_account_balances("thecrazygm")
print(f"Balances for thecrazygm: {balances}")
