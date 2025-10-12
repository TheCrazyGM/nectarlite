from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch

import pytest

from nectarlite.account import Account
from nectarlite.amount import Amount
from nectarlite.api import Api
from nectarlite.transaction import Follow, Transaction


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


@pytest.fixture
def account_with_api():
    api = Mock(spec=Api)
    api.call.return_value = [
        {
            "name": "testaccount",
            "balance": "1.000 HIVE",
            "hbd_balance": "2.000 HBD",
        }
    ]
    return Account("testaccount", api=api)


@patch("nectarlite.account.Transaction")
@patch("nectarlite.account.Follow")
def test_account_follow_method(mock_follow, mock_transaction, account_with_api):
    # Set up mocks
    mock_transaction_instance = Mock(spec=Transaction)
    mock_transaction.return_value = mock_transaction_instance
    mock_follow_instance = Mock(spec=Follow)
    mock_follow.return_value = mock_follow_instance

    # Call the follow method
    tx = account_with_api.follow("target_account")

    # Verify Follow was called with correct parameters
    mock_follow.assert_called_once_with(
        follower="testaccount", following="target_account", what=["blog"]
    )

    # Verify the operation was appended to the transaction
    mock_transaction_instance.append_op.assert_called_once_with(mock_follow_instance)

    # Verify the transaction was returned
    assert tx == mock_transaction_instance


@patch("nectarlite.account.Transaction")
@patch("nectarlite.account.Follow")
def test_account_unfollow_method(mock_follow, mock_transaction, account_with_api):
    # Set up mocks
    mock_transaction_instance = Mock(spec=Transaction)
    mock_transaction.return_value = mock_transaction_instance
    mock_follow_instance = Mock(spec=Follow)
    mock_follow.return_value = mock_follow_instance

    # Call the unfollow method
    tx = account_with_api.unfollow("target_account")

    # Verify Follow was called with empty what list (unfollow)
    mock_follow.assert_called_once_with(
        follower="testaccount", following="target_account", what=[]
    )

    # Verify the operation was appended to the transaction
    mock_transaction_instance.append_op.assert_called_once_with(mock_follow_instance)

    # Verify the transaction was returned
    assert tx == mock_transaction_instance


@patch("nectarlite.account.Transaction")
@patch("nectarlite.account.Follow")
def test_account_ignore_method(mock_follow, mock_transaction, account_with_api):
    # Set up mocks
    mock_transaction_instance = Mock(spec=Transaction)
    mock_transaction.return_value = mock_transaction_instance
    mock_follow_instance = Mock(spec=Follow)
    mock_follow.return_value = mock_follow_instance

    # Call the ignore method
    _tx = account_with_api.ignore("target_account")

    # Verify Follow was called with ["ignore"] what list
    mock_follow.assert_called_once_with(
        follower="testaccount", following="target_account", what=["ignore"]
    )

    # Verify the operation was appended to the transaction
    mock_transaction_instance.append_op.assert_called_once_with(mock_follow_instance)


@patch("nectarlite.account.Transaction")
@patch("nectarlite.account.Follow")
def test_account_unignore_method(mock_follow, mock_transaction, account_with_api):
    # Set up mocks
    mock_transaction_instance = Mock(spec=Transaction)
    mock_transaction.return_value = mock_transaction_instance

    # Create a mock for the unfollow method which unignore calls
    account_with_api.unfollow = Mock(return_value=mock_transaction_instance)

    # Call the unignore method
    tx = account_with_api.unignore("target_account")

    # Verify unfollow was called (unignore is implemented through unfollow)
    account_with_api.unfollow.assert_called_once_with("target_account")

    # Verify the transaction was returned
    assert tx == mock_transaction_instance


@patch("nectarlite.account.HAF")
def test_account_get_reputation(mock_haf):
    mock_haf_instance = mock_haf.return_value
    mock_haf_instance.reputation.return_value = {"reputation": 987654}

    account = Account("testaccount")

    value1 = account.get_reputation()

    mock_haf.assert_called_once_with()
    mock_haf_instance.reputation.assert_called_once_with("testaccount")
    assert value1 == 987654

    # Cached access via property should not trigger an additional fetch
    value2 = account.reputation
    assert value2 == 987654
    mock_haf_instance.reputation.assert_called_once_with("testaccount")

    # Refresh should trigger a new fetch
    mock_haf_instance.reputation.return_value = {"reputation": 123456}
    value3 = account.get_reputation(refresh=True)
    assert value3 == 123456
    assert mock_haf_instance.reputation.call_count == 2

    # Alias property mirrors reputation
    assert account.rep == 123456


def test_account_get_voting_power_without_refresh():
    account = Account("testaccount")
    now = datetime.now(timezone.utc)
    account._data = {
        "voting_manabar": {
            "current_mana": 9000,
            "max_mana": 10000,
            "last_update_time": (now - timedelta(hours=1)).isoformat(),
        }
    }

    vp = account.get_voting_power()
    property_value = account.voting_power
    alias_value = account.vp

    assert 90 < vp <= 100
    assert property_value == pytest.approx(vp, rel=1e-6)
    assert alias_value == pytest.approx(vp, rel=1e-6)


def test_account_get_voting_power_triggers_refresh_when_missing():
    api = Mock(spec=Api)
    account = Account("testaccount", api=api)
    account.refresh = Mock()
    account._data = {}  # ensure empty so refresh is invoked
    account.refresh.side_effect = lambda: account._data.update(
        {
            "voting_manabar": {
                "current_mana": 1000,
                "max_mana": 10000,
                "last_update_time": datetime.now(timezone.utc).isoformat(),
            }
        }
    )

    vp = account.get_voting_power()
    account.refresh.assert_called_once()
    assert isinstance(vp, float)


def test_account_get_rc_info_and_caching():
    api = Mock(spec=Api)
    now = datetime.now(timezone.utc)
    last_update = int((now - timedelta(hours=2)).timestamp())
    api.call.return_value = {
        "rc_accounts": [
            {
                "max_rc": "200000",
                "rc_manabar": {
                    "current_mana": "100000",
                    "last_update_time": last_update,
                },
            }
        ]
    }

    account = Account("testaccount", api=api)

    info = account.get_rc_info()
    api.call.assert_called_once_with(
        "rc_api", "find_rc_accounts", [{"accounts": ["testaccount"]}]
    )
    assert info is account.rc_info
    assert info["max_mana"] == 200000
    assert info["last_mana"] == 100000
    assert info["current_mana"] >= 100000
    assert 0 <= account.rc <= 100

    api.call.reset_mock()
    cached = account.get_rc_info()
    api.call.assert_not_called()
    assert cached is info

    api.call.return_value = {
        "rc_accounts": [
            {
                "max_rc": "200000",
                "rc_manabar": {
                    "current_mana": "150000",
                    "last_update_time": last_update,
                },
            }
        ]
    }

    refreshed = account.get_rc_info(refresh=True)
    api.call.assert_called_once()
    assert refreshed["last_mana"] == 150000
