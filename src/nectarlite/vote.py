"""CommentVote model for interacting with Hive votes."""

import logging

from .exceptions import NodeError

log = logging.getLogger(__name__)


class CommentVote:
    """CommentVote class for interacting with Hive votes."""

    def __init__(self, voter, author, permlink, api=None):
        """Initialize the comment vote wrapper."""
        self.voter = voter
        self.author = author
        self.permlink = permlink
        self.api = api
        self._data = {}

        self._amount_fields = set()

    def refresh(self):
        """Fetch the vote data from the blockchain."""
        if not self.api:
            log.error(
                "Cannot refresh vote %s on %s/%s: API not configured.",
                self.voter,
                self.author,
                self.permlink,
            )
            raise ValueError("API not configured.")

        log.debug(
            "Requesting vote data for %s on %s/%s.",
            self.voter,
            self.author,
            self.permlink,
        )
        try:
            active_votes = self.api.call(
                "condenser_api", "get_active_votes", [self.author, self.permlink]
            )
        except Exception as exc:  # noqa: BLE001 - surface as NodeError
            if isinstance(exc, NodeError):
                raise
            log.error(
                "Error retrieving vote %s on %s/%s: %s",
                self.voter,
                self.author,
                self.permlink,
                exc,
            )
            raise NodeError(str(exc)) from exc
        vote_data = None
        for v in active_votes:
            if v["voter"] == self.voter:
                vote_data = v
                break

        if not vote_data:
            log.warning(
                "Vote %s on %s/%s not found.",
                self.voter,
                self.author,
                self.permlink,
            )
            raise ValueError(
                f"Vote from {self.voter} on @{self.author}/{self.permlink} not found."
            )
        self._data = vote_data

    def __getattr__(self, key):
        """Get an attribute from the vote data, fetching if necessary."""
        if key == "_data" or key not in self.__dict__:
            if not self._data:
                self.refresh()

        if key not in self._data:
            raise AttributeError(
                f"'{self.__class__.__name__}' object has no attribute '{key}'"
            )

        return self._data[key]

    def __getitem__(self, key):
        """Allow dictionary-style access to the raw vote data."""
        if not self._data:
            self.refresh()
        return self._data.get(key)

    def __str__(self):
        return f"<CommentVote voter={self.voter} author={self.author} permlink={self.permlink}>"
