"""Vote class for interacting with Hive votes."""


class Vote:
    """Vote class for interacting with Hive votes."""

    def __init__(self, voter, author, permlink, api=None):
        """Initialize the Vote class.

        :param str voter: The voter.
        :param str author: The author of the comment or post.
        :param str permlink: The permlink of the comment or post.
        :param Api api: An instance of the Api class.
        """
        self.voter = voter
        self.author = author
        self.permlink = permlink
        self.api = api
        self._data = {}

        self._amount_fields = set()

    def refresh(self):
        """Fetch the vote data from the blockchain."""
        if not self.api:
            raise ValueError("API not configured.")

        active_votes = self.api.call(
            "condenser_api", "get_active_votes", [self.author, self.permlink]
        )
        vote_data = None
        for v in active_votes:
            if v["voter"] == self.voter:
                vote_data = v
                break

        if not vote_data:
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
        return f"<Vote by {self.voter} on @{self.author}/{self.permlink}>"
