# Nectarlite

Nectarlite is a lightweight Python library for interacting with the Hive blockchain. It focuses on providing core API access and transaction signing capabilities without unnecessary overhead.

## Features

- **Lightweight:** Designed to be lean and efficient.
- **API Communication:** Easily make RPC calls to Hive nodes.
- **Transaction Building & Signing:** Construct and sign Hive transactions.
- **High-Level Abstractions:** Simple classes for Account, Comment, Vote, Asset, and Amount.
- **HAF Integration:** Access to the Hive Account Feed (HAF) for advanced queries.
- **Memo Encryption:** Encrypt and decrypt memos for private communication.

## Installation

```bash
pip install nectarlite
```

## Usage

### Initializing the API

```python
from nectarlite import Api

nodes = ["https://api.hive.blog", "https://api.syncad.com"]
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

# Get a comment (replace with a real author and permlink)
comment = Comment(author="gtg", permlink="this-is-a-test-post", api=api)
print(f"Title: {comment.title}")

# Get a vote on that comment (replace with a real voter)
vote = Vote(voter="somevoter", author="gtg", permlink="this-is-a-test-post", api=api)
print(f"Voter: {vote.voter}")
```

### Using the HAF API

```python
from nectarlite import HAF

haf = HAF()

# Get an account's reputation
reputation = haf.reputation("your_account_name")
print(f"Reputation: {reputation['reputation']}")
```

### Creating and Broadcasting a Transfer with an Encrypted Memo

```python
from nectarlite import Account, Api, Memo, Transaction, Transfer, Wallet

# 1. Setup
api = Api()
wallet = Wallet()

# Add your private keys to the in-memory wallet
# IMPORTANT: In a real application, load these securely (e.g., from environment variables)
sender_active_wif = "5J..."
_wif = "5J..."
wallet.add_key("your-sender-account", "active", sender_active_wif)
wallet.add_key("your-sender-account", "memo", sender_memo_wif)

# 2. Create the Memo Object
from_account = Account("your-sender-account", api=api)
to_account = Account("recipient-account", api=api)
memo = Memo(from_account=from_account, to_account=to_account, wallet=wallet, api=api)

# 3. Encrypt the Memo
memo_text = "This is a top-secret message!"
encrypted_memo = memo.encrypt(memo_text)

# 4. Create and Sign the Transaction
tx = Transaction(api=api)
tx.append_op(
    Transfer(
        frm="your-sender-account",
        to="recipient-account",
        amount="0.001 HIVE",
        memo=encrypted_memo,
    )
)
tx.sign(sender_active_wif) # Sign with the active key

# 5. Broadcast the Transaction
response = tx.broadcast()
print(f"Transaction Broadcast Response: {response}")
```
