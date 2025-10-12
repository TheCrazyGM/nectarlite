#!/usr/bin/env python
"""
Example of using the Follow operation in nectarlite.

This script demonstrates how to follow, unfollow, ignore, and unignore
accounts on the Hive blockchain using nectarlite.

Note: This example doesn't broadcast transactions to protect users from
accidental operations. To broadcast, uncomment the tx.broadcast() line
and replace the sample keys with real keys.
"""

from nectarlite import Account, Api, Wallet

# Connect to Hive nodes
api = Api(["https://api.hive.blog", "https://api.syncad.com"])

# Sample account - replace with your own account
account_name = "your_account_name"

# Initialize wallet for signing
wallet = Wallet()

# In a real application, load this securely from a secure source
# This is for demonstration only - the key shown here is invalid
posting_key = "5Jxxxx..."

# Add the key to the wallet
# wallet.add_key(account_name, "posting", posting_key)

# Initialize the account
account = Account(account_name, api=api)


def follow_example(account_to_follow="hivebuzz"):
    """Follow an account example."""
    print(f"Creating a transaction to follow @{account_to_follow}...")

    # Use the helper method in the Account class
    tx = account.follow(account_to_follow)

    # Sign with the posting key
    # tx.sign(wallet.get_key(account_name, "posting"))

    print("Transaction created! To broadcast (not executed in this demo):")
    print("tx.sign(wallet.get_key(account_name, 'posting'))")
    print("tx.broadcast()")

    # Uncomment to actually broadcast the transaction
    # response = tx.broadcast()
    # print(f"Transaction broadcast response: {response}")

    return tx


def unfollow_example(account_to_unfollow="hivebuzz"):
    """Unfollow an account example."""
    print(f"Creating a transaction to unfollow @{account_to_unfollow}...")

    # Use the helper method
    tx = account.unfollow(account_to_unfollow)

    print("Transaction created! To broadcast (not executed in this demo):")
    print("tx.sign(wallet.get_key(account_name, 'posting'))")
    print("tx.broadcast()")

    return tx


def ignore_example(account_to_ignore="spammer"):
    """Mute/ignore an account example."""
    print(f"Creating a transaction to ignore @{account_to_ignore}...")

    # Use the helper method
    tx = account.ignore(account_to_ignore)

    print("Transaction created! To broadcast (not executed in this demo):")
    print("tx.sign(wallet.get_key(account_name, 'posting'))")
    print("tx.broadcast()")

    return tx


def unignore_example(account_to_unignore="spammer"):
    """Unmute an account example."""
    print(f"Creating a transaction to unignore @{account_to_unignore}...")

    # Use the helper method
    tx = account.unignore(account_to_unignore)

    print("Transaction created! To broadcast (not executed in this demo):")
    print("tx.sign(wallet.get_key(account_name, 'posting'))")
    print("tx.broadcast()")

    return tx


if __name__ == "__main__":
    print("=== Nectarlite Follow Operations Example ===")

    print("\n1. Follow Example")
    follow_tx = follow_example()

    print("\n2. Unfollow Example")
    unfollow_tx = unfollow_example()

    print("\n3. Ignore/Mute Example")
    ignore_tx = ignore_example()

    print("\n4. Unignore/Unmute Example")
    unignore_tx = unignore_example()

    print("\n=== End of Examples ===")
