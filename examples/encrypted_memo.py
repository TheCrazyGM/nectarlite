#!/usr/bin/env python

import os

from nectarlite import Account, Api, Memo, Transaction, Transfer, Wallet

# --- Configuration ---
SENDER_ACCOUNT = "your-sender-account"  # Replace with your Hive account name
RECIPIENT_ACCOUNT = (
    "recipient-account"  # Replace with the recipient's Hive account name
)
# In a real application, load these securely (e.g., from environment variables)
# For this example, we'll try to get them from environment variables.
# IMPORTANT: Do not hardcode your private keys in production code.
SENDER_ACTIVE_WIF = os.environ.get("SENDER_ACTIVE_WIF")
SENDER_MEMO_WIF = os.environ.get("SENDER_MEMO_WIF")


# --- Main Script ---
def main():
    if not all([SENDER_ACCOUNT, RECIPIENT_ACCOUNT, SENDER_ACTIVE_WIF, SENDER_MEMO_WIF]):
        print(
            "Please set the SENDER_ACCOUNT, RECIPIENT_ACCOUNT, SENDER_ACTIVE_WIF, and SENDER_MEMO_WIF environment variables."
        )
        return

    # 1. Setup
    print("Initializing API and Wallet...")
    api = Api(nodes=["https://api.hive.blog", "https://api.syncad.com"])
    wallet = Wallet()

    # Add keys to the in-memory wallet
    wallet.add_key(SENDER_ACCOUNT, "active", SENDER_ACTIVE_WIF)
    wallet.add_key(SENDER_ACCOUNT, "memo", SENDER_MEMO_WIF)
    print("Wallet configured.")

    # 2. Create the Memo Object
    from_account = Account(SENDER_ACCOUNT, api=api)
    to_account = Account(RECIPIENT_ACCOUNT, api=api)
    memo = Memo(
        from_account=from_account, to_account=to_account, wallet=wallet, api=api
    )

    # 3. Encrypt the Memo
    memo_text = f"This is a secret message sent at {api.get_dynamic_global_properties()['time']}"
    print(f"Encrypting memo: '{memo_text}'")
    encrypted_memo = memo.encrypt(memo_text)
    print(f"Encrypted Memo: {encrypted_memo}")

    # 4. Create and Sign the Transaction
    print("\nCreating and signing the transaction...")
    tx = Transaction(api=api)
    op = Transfer(
        frm=SENDER_ACCOUNT,
        to=RECIPIENT_ACCOUNT,
        amount="0.001",
        asset="HIVE",
        memo=encrypted_memo,
    )
    tx.append_op(op)
    tx.sign(SENDER_ACTIVE_WIF)
    print("Transaction signed.")

    # 5. Broadcast the Transaction
    print("Broadcasting the transaction...")
    try:
        response = tx.broadcast()
        print("\nTransaction successfully broadcasted!")
        print(f"Transaction ID: {response['id']}")
        print(f"Block Number: {response['block_num']}")
    except Exception as e:
        print(f"\nAn error occurred while broadcasting: {e}")


if __name__ == "__main__":
    main()
