# Nectarlite

Nectarlite is a lightweight Python library for interacting with the Hive blockchain. It focuses on providing core API access and transaction signing capabilities without unnecessary overhead.

## Features

- **Lightweight:** Designed to be lean and efficient.
- **API Communication:** Easily make RPC calls to Hive nodes.
- **Transaction Building & Signing:** Construct and sign Hive transactions.
- **High-Level Abstractions:** Simple classes for Account, Comment, Vote, Asset, and Amount.
- **Account Insights:** Built-in helpers for reputation, voting power, and resource credits.
- **HAF Integration:** Access to the Hive Account Feed (HAF) for advanced queries.
- **Memo Encryption:** Encrypt and decrypt memos for private communication.
- **Real-Time Stream:** Stream blocks and operations as they happen.

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
print(f"Reputation: {account.reputation}")
print(f"Voting Power: {account.voting_power:.2f}%")
print(f"Resource Credits: {account.rc if account.rc is not None else 'unavailable'}")

# Inspect detailed RC information when available
rc_details = account.rc_info
if rc_details:
    for key, value in rc_details.items():
        print(key, value)
```

### Streaming Live Blockchain Events

Listen for all new votes on the Hive blockchain in real-time.

```python
from nectarlite import Api, Stream

# We use 'head' mode to get events as soon as they are broadcast
listener = Stream(api=Api(["https://api.hive.blog"]), blockchain_mode="head")

print("Listening for new votes... (Press Ctrl+C to stop)")
for vote in listener.on("vote"):
    voter = vote["op"][1]["voter"]
    author = vote["op"][1]["author"]
    print(f"New Vote! Voter: {voter}, Post: @{author}/{vote["op"][1]["permlink"]}")
```

### Creating and Broadcasting a Transfer with an Encrypted Memo

Set the `ACTIVE_WIF` and `MEMO_WIF` environment variables before running the example:

```bash
export ACTIVE_WIF="5J..."
export MEMO_WIF="5J..."
```

```python
import os

from nectarlite import Account, Api, Memo, Transaction, Transfer, Wallet

# 1. Setup
api = Api(nodes="https://api.hive.blog")
wallet = Wallet()

sender_account = "your-sender-account"
recipient_account = "recipient-account"
sender_active_wif = os.environ["ACTIVE_WIF"]
sender_memo_wif = os.environ["MEMO_WIF"]

wallet.add_key(sender_account, "active", sender_active_wif)
wallet.add_key(sender_account, "memo", sender_memo_wif)

# 2. Create the Memo Object and Encrypt
from_account = Account(sender_account, api=api)
to_account = Account(recipient_account, api=api)
memo = Memo(from_account, to_account, wallet, api)
encrypted_memo = memo.encrypt("This is a secret message!")

# 3. Create and Sign the Transaction
tx = Transaction(api=api)
tx.append_op(
    Transfer(
        frm=from_account.name,
        to=to_account.name,
        amount="0.001",
        asset="HIVE",
        memo=encrypted_memo,
    )
)
tx.sign(sender_active_wif) # Sign with the active key

# 4. Broadcast the Transaction
response = tx.broadcast()
print(f"Transaction Broadcast Response: {response}")
```
