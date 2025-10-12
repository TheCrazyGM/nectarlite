from nectarlite import Api, Transaction, Transfer, Wallet

nodes = ["https://api.hive.blog", "https://api.syncad.com"]
api = Api(nodes)

# Create wallet and load your key
wallet = Wallet()
# !!! WARNING: Replace with your actual WIF (active key recommended for transfers) !!!
# !!! Do NOT commit real keys to git! Use env vars or input in production.        !!!
wallet.add_key("your_account_name", "active", "5J...")  # Your WIF here

# Replace with details
from_account = "your_account_name"
to_account = "recipient_account"
amount_to_transfer = "0.001"
asset_symbol = "HIVE"
memo_text = "Test transfer using Nectarlite Wallet!"

try:
    tx = Transaction(api=api)
    tx.append_op(
        Transfer(
            frm=from_account,
            to=to_account,
            amount=amount_to_transfer,
            asset=asset_symbol,
            memo=memo_text,
        )
    )
    # Sign using wallet
    wallet.sign(tx, from_account, "active")
    response = tx.broadcast()
    print(f"Transaction Broadcast Response: {response}")
except Exception as e:
    print(f"Error broadcasting transaction: {e}")
