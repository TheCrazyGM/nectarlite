from unittest.mock import patch

from nectarlite.haf import HAF


@patch("requests.request")
def test_haf_reputation_dict_response(mock_request):
    mock_request.return_value.json.return_value = {
        "reputation": 75,
        "account": "testaccount",
    }
    haf = HAF()
    response = haf.reputation("testaccount")

    assert response["reputation"] == 75
    assert response["account"] == "testaccount"
    mock_request.assert_called_once_with(
        "GET",
        "https://api.hive.blog/reputation-api/accounts/testaccount/reputation",
        headers={"accept": "application/json", "User-Agent": "nectarlite/0.0.1"},
        timeout=30.0,
    )


@patch("requests.request")
def test_haf_reputation_int_response(mock_request):
    mock_request.return_value.json.return_value = 75
    haf = HAF()
    response = haf.reputation("testaccount")

    assert response["reputation"] == 75
    assert response["account"] == "testaccount"
    mock_request.assert_called_once_with(
        "GET",
        "https://api.hive.blog/reputation-api/accounts/testaccount/reputation",
        headers={"accept": "application/json", "User-Agent": "nectarlite/0.0.1"},
        timeout=30.0,
    )


@patch("requests.request")
def test_haf_account_balances(mock_request):
    mock_request.return_value.json.return_value = {"balance": "1.000 HIVE"}
    haf = HAF()
    response = haf.get_account_balances("testaccount")

    assert response["balance"] == "1.000 HIVE"
    mock_request.assert_called_once_with(
        "GET",
        "https://api.hive.blog/balance-api/accounts/testaccount/balances",
        headers={"accept": "application/json", "User-Agent": "nectarlite/0.0.1"},
        timeout=30.0,
    )
