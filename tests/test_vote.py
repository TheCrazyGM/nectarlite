from unittest.mock import Mock

import pytest

from nectarlite.vote import Vote
from nectarlite.api import Api


@pytest.fixture
def mock_api():
    api = Mock(spec=Api)
    api.call.return_value = [
        {
            "voter": "testvoter",
            "author": "testauthor",
            "permlink": "test-permlink",
            "weight": 10000,
        }
    ]
    return api


def test_vote_dynamic_attributes(mock_api):
    vote = Vote("testvoter", "testauthor", "test-permlink", api=mock_api)

    # Test dynamic attributes
    assert vote.voter == "testvoter"
    assert vote.author == "testauthor"
    assert vote.permlink == "test-permlink"
    assert vote.weight == 10000

    # Test that the API was called only once
    mock_api.call.assert_called_once_with(
        "condenser_api", "get_active_votes", ["testauthor", "test-permlink"]
    )
