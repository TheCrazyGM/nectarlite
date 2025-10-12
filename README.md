# Nectarlite

Nectarlite is a lightweight Python library for interacting with the Hive blockchain. It focuses on providing core API access and transaction signing capabilities without unnecessary overhead.

## Features

- **Lightweight:** Designed to be lean and efficient.
- **API Communication:** Easily make RPC calls to Hive nodes.
- **Transaction Building & Signing:** Construct and sign Hive transactions.
- **High-Level Abstractions:** Simple classes for Account, Block, Asset, and Amount.

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
account.refresh()
print(f"Account Name: {account.name}")
print(f"Balance: {account['balance']}")
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
