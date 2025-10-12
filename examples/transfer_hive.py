import os

from nectarlite import Account, Api, Memo, Transaction, Transfer, Wallet

# Set these environment variables before running the script:
#   export ACTIVE_WIF="5J..."
#   export MEMO_WIF="5J..."

SENDER_ACCOUNT = "your-sender-account"
RECIPIENT_ACCOUNT = "recipient-account"


def main():
    sender_active_wif = os.environ.get("ACTIVE_WIF")
    sender_memo_wif = os.environ.get("MEMO_WIF")

    if not sender_active_wif or not sender_memo_wif:
        raise SystemExit("Please set ACTIVE_WIF and MEMO_WIF environment variables")

    api = Api(nodes="https://api.hive.blog")
    wallet = Wallet()

    wallet.add_key(SENDER_ACCOUNT, "active", sender_active_wif)
    wallet.add_key(SENDER_ACCOUNT, "memo", sender_memo_wif)

    from_account = Account(SENDER_ACCOUNT, api=api)
    to_account = Account(RECIPIENT_ACCOUNT, api=api)
    memo = Memo(from_account, to_account, wallet, api)
    encrypted_memo = memo.encrypt("This is a secret message!")

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

    wallet.sign(tx, SENDER_ACCOUNT, "active")
    # or
    # tx.sign(sender_active_wif)
    response = tx.broadcast()
    print(f"Transaction Broadcast Response: {response}")


if __name__ == "__main__":
    main()
