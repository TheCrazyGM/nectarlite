#!/usr/bin/env python3
import os

from nectarlite import Account, Api, Memo, Transaction, Transfer, Wallet

# 1. Setup
api = Api(nodes=["https://api.hive.blog", "https://api.syncad.com"])
wallet = Wallet()

# Add your private keys to the in-memory wallet
# IMPORTANT: In a real application, load these securely
sender_active_wif = os.environ.get("ACTIVE_WIF")
sender_memo_wif = os.environ.get("MEMO_WIF")
wallet.add_key("thecrazygm", "active", sender_active_wif)
wallet.add_key("thecrazygm", "memo", sender_memo_wif)

# 2. Create the Memo Object and Encrypt
from_account = Account("thecrazygm", api=api)
to_account = Account("ecoinstant", api=api)
memo = Memo(from_account, to_account, wallet, api)
encrypted_memo = memo.encrypt("The Crow Flies at Midnight.")

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
# tx.sign(sender_active_wif)  # Sign with the active key
wallet.sign(tx, from_account.name, "active")  # Sign with the wallet
print(tx._construct_tx())
# 4. Broadcast the Transaction
# response = tx.broadcast()
# print(f"Transaction Broadcast Response: {response}")
