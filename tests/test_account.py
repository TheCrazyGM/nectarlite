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
        follower="testaccount", 
        following="target_account", 
        what=["blog"]
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
        follower="testaccount", 
        following="target_account", 
        what=[]
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
        follower="testaccount", 
        following="target_account", 
        what=["ignore"]
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
