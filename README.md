# Nectarlite

Nectarlite is a lightweight Python library for interacting with the Hive blockchain. It focuses on providing core API access and transaction signing capabilities without unnecessary overhead.

## Features

- **Lightweight:** Designed to be lean and efficient.
- **API Communication:** Easily make RPC calls to Hive nodes.
- **Transaction Building & Signing:** Construct and sign Hive transactions.
- **High-Level Abstractions:** Simple classes for Account, Comment, Vote, Asset, and Amount.
- **HAF Integration:** Access to the Hive Account Feed (HAF) for advanced queries.

## Installation

```bash
pip install nectarlite
```

## Usage

### Initializing the API

```python
from nectarlite import Api

nodes = ["https://api.hive.blog", "https://api.openhive.network"]
api = Api(nodes)
```

### Getting Account Information

```python
from nectarlite import Account

account = Account("your_account_name", api=api)

# The account data is automatically fetched when you access an attribute
print(f"Account Name: {account.name}")
print(f"Balance: {account.balance}")
print(f"Vesting Shares: {account.vesting_shares}")
```

### Getting Comment and Vote Information

```python
from nectarlite import Comment, Vote

# Get a comment
comment = Comment(author="testauthor", permlink="test-permlink", api=api)
print(f"Title: {comment.title}")
print(f"Author: {comment.author}")
print(f"Pending Payout: {comment.pending_payout_value}")

# Get a vote
vote = Vote(voter="testvoter", author="testauthor", permlink="test-permlink", api=api)
print(f"Voter: {vote.voter}")
print(f"Weight: {vote.weight}")
```

### Using the HAF API

```python
from nectarlite import HAF

haf = HAF()

# Get an account's reputation
reputation = haf.reputation("your_account_name")
print(f"Reputation: {reputation['reputation']}")

# Get an account's balances
balances = haf.get_account_balances("your_account_name")
print(f"HIVE Balance: {balances['hive_balance']}")
```

### Creating and Broadcasting a Transfer Transaction

```python
from nectarlite import Transaction, Transfer

# Replace with your actual private key (WIF format)
private_key = "5J..."

tx = Transaction(api=api)
tx.append_op(Transfer(frm="your_account_name", to="recipient_account", amount="1.000", asset="HIVE"))
tx.sign(private_key)
response = tx.broadcast()
print(f"Transaction Broadcast Response: {response}")
```
