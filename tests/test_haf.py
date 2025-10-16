from unittest.mock import MagicMock, patch

from nectarlite.haf import HAF


def _setup_client_mock(mock_client_cls):
    mock_client = MagicMock()
    mock_client_cls.return_value.__enter__.return_value = mock_client
    mock_client_cls.return_value.__exit__.return_value = None
    return mock_client


@patch("httpx.Client")
def test_haf_reputation_dict_response(mock_client_cls):
    mock_client = _setup_client_mock(mock_client_cls)
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "reputation": 75,
        "account": "testaccount",
    }
    mock_response.raise_for_status.return_value = None
    mock_client.request.return_value = mock_response

    haf = HAF()
    response = haf.reputation("testaccount")

    assert response["reputation"] == 75
    assert response["account"] == "testaccount"
    mock_client_cls.assert_called_once_with(timeout=30.0)
    mock_client.request.assert_called_once_with(
        "GET",
        "https://api.hive.blog/reputation-api/accounts/testaccount/reputation",
        headers={"accept": "application/json", "User-Agent": "nectarlite/0.0.1"},
    )


@patch("httpx.Client")
def test_haf_reputation_int_response(mock_client_cls):
    mock_client = _setup_client_mock(mock_client_cls)
    mock_response = MagicMock()
    mock_response.json.return_value = 75
    mock_response.raise_for_status.return_value = None
    mock_client.request.return_value = mock_response

    haf = HAF()
    response = haf.reputation("testaccount")

    assert response["reputation"] == 75
    assert response["account"] == "testaccount"
    mock_client_cls.assert_called_once_with(timeout=30.0)
    mock_client.request.assert_called_once_with(
        "GET",
        "https://api.hive.blog/reputation-api/accounts/testaccount/reputation",
        headers={"accept": "application/json", "User-Agent": "nectarlite/0.0.1"},
    )


@patch("httpx.Client")
def test_haf_account_balances(mock_client_cls):
    mock_client = _setup_client_mock(mock_client_cls)
    mock_response = MagicMock()
    mock_response.json.return_value = {"balance": "1.000 HIVE"}
    mock_response.raise_for_status.return_value = None
    mock_client.request.return_value = mock_response

    haf = HAF()
    response = haf.get_account_balances("testaccount")

    assert response["balance"] == "1.000 HIVE"
    mock_client_cls.assert_called_once_with(timeout=30.0)
    mock_client.request.assert_called_once_with(
        "GET",
        "https://api.hive.blog/balance-api/accounts/testaccount/balances",
        headers={"accept": "application/json", "User-Agent": "nectarlite/0.0.1"},
    )
