from nectarlite import Api, Transaction, Transfer

nodes = ["https://api.hive.blog", "https://api.openhive.network"]
api = Api(nodes)

# !!! WARNING: Replace with your actual private key (WIF format) !!!
# !!!          Do NOT use your owner key for this example.       !!!
# !!!          Use an active or posting key with limited funds.  !!!
private_key = "5J..."

# Replace with your account name and recipient
from_account = "your_account_name"
to_account = "recipient_account"
amount_to_transfer = "0.001"
asset_symbol = "HIVE"
memo_text = "Test transfer from nectarlite"

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
    tx.sign(private_key)
    response = tx.broadcast()
    print(f"Transaction Broadcast Response: {response}")
except Exception as e:
    print(f"Error broadcasting transaction: {e}")
