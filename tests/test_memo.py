from unittest.mock import Mock

import pytest

from nectarlite.account import Account
from nectarlite.api import Api
from nectarlite.crypto.keys import PrivateKey
from nectarlite.memo import Memo
from nectarlite.wallet import Wallet


@pytest.fixture
def mock_config():
    """Provides mock keys and account info for the tests."""
    from_key = PrivateKey(b"\x01" * 32)
    to_key = PrivateKey(b"\x02" * 32)

    return {
        "from_account": {
            "name": "from-user",
            "priv_key": from_key,
            "pub_key": str(from_key.pubkey),
        },
        "to_account": {
            "name": "to-user",
            "priv_key": to_key,
            "pub_key": str(to_key.pubkey),
        },
    }


@pytest.fixture
def mock_api(mock_config):
    """Mocks the API to return account data for both sender and receiver."""
    api = Mock(spec=Api)

    def call_side_effect(api_name, method, params):
        if method == "get_accounts":
            account_name = params[0][0]
            if account_name == mock_config["from_account"]["name"]:
                return [
                    {
                        "name": account_name,
                        "memo_key": mock_config["from_account"]["pub_key"],
                    }
                ]
            if account_name == mock_config["to_account"]["name"]:
                return [
                    {
                        "name": account_name,
                        "memo_key": mock_config["to_account"]["pub_key"],
                    }
                ]
        return {}

    api.call.side_effect = call_side_effect
    return api


def test_memo_encryption_and_decryption(mock_config, mock_api):
    """Tests the full memo workflow: encrypt with sender's key, decrypt with receiver's key."""
    # 1. Setup Sender's Wallet and Memo Object
    sender_wallet = Mock(spec=Wallet)
    sender_wallet.get_private_key.return_value = mock_config["from_account"]["priv_key"]

    from_account = Account(mock_config["from_account"]["name"], api=mock_api)
    to_account = Account(mock_config["to_account"]["name"], api=mock_api)

    memo_to_encrypt = Memo(
        from_account=from_account,
        to_account=to_account,
        wallet=sender_wallet,
        api=mock_api,
    )

    # 2. Encrypt the memo
    memo_text = "This is a secret message."
    encrypted_memo = memo_to_encrypt.encrypt(memo_text)
    assert encrypted_memo.startswith("#")

    # 3. Setup Receiver's Wallet and Memo Object for Decryption
    receiver_wallet = Mock(spec=Wallet)
    receiver_wallet.get_private_key.return_value = mock_config["to_account"]["priv_key"]

    memo_to_decrypt = Memo(
        from_account=from_account,
        to_account=to_account,
        wallet=receiver_wallet,
        api=mock_api,
    )

    # 4. Decrypt the memo
    decrypted_memo = memo_to_decrypt.decrypt(encrypted_memo)

    # 5. Verify the result
    assert decrypted_memo == memo_text
