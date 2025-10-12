from unittest.mock import Mock

import pytest

from nectarlite.account import Account
from nectarlite.amount import Amount
from nectarlite.api import Api


@pytest.fixture
def mock_api():
    api = Mock(spec=Api)
    api.call.return_value = [
        {
            "name": "testaccount",
            "balance": "1.000 HIVE",
            "hbd_balance": "2.000 HBD",
            "vesting_shares": "1000.000000 VESTS",
        }
    ]
    return api


def test_account_dynamic_attributes(mock_api):
    account = Account("testaccount", api=mock_api)

    # Test dynamic attributes
    assert account.name == "testaccount"
    assert isinstance(account.balance, Amount)
    assert account.balance.amount == 1.0
    assert account.balance.asset.symbol == "HIVE"
    assert isinstance(account.hbd_balance, Amount)
    assert account.hbd_balance.amount == 2.0
    assert account.hbd_balance.asset.symbol == "HBD"
    assert isinstance(account.vesting_shares, Amount)
    assert account.vesting_shares.amount == 1000.0
    assert account.vesting_shares.asset.symbol == "VESTS"

    # Test that the API was called only once
    mock_api.call.assert_called_once_with(
        "condenser_api", "get_accounts", [["testaccount"]]
    )
