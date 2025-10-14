"""Comment class for interacting with Hive comments and posts."""

from .amount import Amount
from .exceptions import NodeError


class Comment:
    """Comment class for interacting with Hive comments and posts."""

    def __init__(self, author, permlink, api=None):
        """Initialize the Comment class.

        :param str author: The author of the comment or post.
        :param str permlink: The permlink of the comment or post.
        :param Api api: An instance of the Api class.
        """
        self.author = author
        self.permlink = permlink
        self.api = api
        self._data = {}

        self._amount_fields = {
            "total_payout_value",
            "max_accepted_payout",
            "pending_payout_value",
            "curator_payout_value",
            "total_pending_payout_value",
            "promoted",
        }

    def refresh(self):
        """Fetch the comment data from the blockchain."""
        if not self.api:
            raise ValueError("API not configured.")

        try:
            content = self.api.call(
                "condenser_api", "get_content", [self.author, self.permlink]
            )
        except Exception as exc:  # noqa: BLE001 - surface as NodeError
            if isinstance(exc, NodeError):
                raise
            raise NodeError(str(exc)) from exc
        if not content or not content["author"]:
            raise ValueError(f"Comment @{self.author}/{self.permlink} not found.")
        self._data = content

    def __getattr__(self, key):
        """Get an attribute from the comment data, fetching if necessary."""
        if key == "_data" or key not in self.__dict__:
            if not self._data:
                self.refresh()

        if key not in self._data:
            raise AttributeError(
                f"'{self.__class__.__name__}' object has no attribute '{key}'"
            )

        value = self._data[key]

        if key in self._amount_fields:
            try:
                amount, asset = value.split()
                return Amount(float(amount), asset, api=self.api)
            except (ValueError, IndexError):
                return value

        return value

    def __getitem__(self, key):
        """Allow dictionary-style access to the raw comment data."""
        if not self._data:
            self.refresh()
        return self._data.get(key)

    def __str__(self):
        return f"<Comment @{self.author}/{self.permlink}>"
