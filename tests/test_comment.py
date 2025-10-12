from unittest.mock import Mock

import pytest

from nectarlite.amount import Amount
from nectarlite.api import Api
from nectarlite.comment import Comment


@pytest.fixture
def mock_api():
    api = Mock(spec=Api)
    api.call.return_value = {
        "author": "testauthor",
        "permlink": "test-permlink",
        "total_payout_value": "10.000 HBD",
        "pending_payout_value": "5.000 HBD",
    }
    return api


def test_comment_dynamic_attributes(mock_api):
    comment = Comment("testauthor", "test-permlink", api=mock_api)

    # Test dynamic attributes
    assert comment.author == "testauthor"
    assert comment.permlink == "test-permlink"
    assert isinstance(comment.total_payout_value, Amount)
    assert comment.total_payout_value.amount == 10.0
    assert comment.total_payout_value.asset.symbol == "HBD"
    assert isinstance(comment.pending_payout_value, Amount)
    assert comment.pending_payout_value.amount == 5.0
    assert comment.pending_payout_value.asset.symbol == "HBD"

    # Test that the API was called only once
    mock_api.call.assert_called_once_with(
        "condenser_api", "get_content", ["testauthor", "test-permlink"]
    )
