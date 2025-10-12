from unittest.mock import Mock

import pytest

from nectarlite.api import Api
from nectarlite.exceptions import InvalidKeyFormatError, MissingKeyError
from nectarlite.transaction import Transaction
from nectarlite.wallet import Wallet


class TestWallet:
    def test_add_key(self):
        wallet = Wallet()
        wallet.add_key(
            "test", "posting", "5Kb8kLf9zgWQnogidDA76MzPL6TsZZY36hWXMssSzNydYXYB9KF"
        )
        assert wallet.has_key("test", "posting")
        assert (
            wallet.get_key("test", "posting")
            == "5Kb8kLf9zgWQnogidDA76MzPL6TsZZY36hWXMssSzNydYXYB9KF"
        )

    def test_add_key_invalid_wif(self):
        wallet = Wallet()
        with pytest.raises(InvalidKeyFormatError):
            wallet.add_key("test", "posting", "K...")  # Not starting with 5
        with pytest.raises(InvalidKeyFormatError):
            wallet.add_key("test", "posting", "invalidbase58")

    def test_has_key(self):
        wallet = Wallet()
        assert not wallet.has_key("test", "posting")
        wallet.add_key(
            "test", "posting", "5Kb8kLf9zgWQnogidDA76MzPL6TsZZY36hWXMssSzNydYXYB9KF"
        )
        assert wallet.has_key("test", "posting")

    def test_get_key_missing(self):
        wallet = Wallet()
        assert wallet.get_key("test", "posting") is None
        wallet.add_key(
            "test", "posting", "5Kb8kLf9zgWQnogidDA76MzPL6TsZZY36hWXMssSzNydYXYB9KF"
        )
        assert wallet.get_key("test", "active") is None

    def test_sign(self):
        wallet = Wallet()
        wallet.add_key(
            "test", "active", "5Kb8kLf9zgWQnogidDA76MzPL6TsZZY36hWXMssSzNydYXYB9KF"
        )

        # Mock Transaction
        api = Mock(spec=Api)
        tx = Mock(spec=Transaction)
        tx.api = api
        tx.sign = Mock()

        wallet.sign(tx, "test", "active")
        tx.sign.assert_called_once_with(
            "5Kb8kLf9zgWQnogidDA76MzPL6TsZZY36hWXMssSzNydYXYB9KF"
        )

        with pytest.raises(MissingKeyError):
            wallet.sign(tx, "test", "memo")
