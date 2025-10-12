"""Account class for interacting with Hive accounts."""


class Account:
    """Account class for interacting with Hive accounts."""

    def __init__(self, account_name, api=None):
        """Initialize the Account class.

        :param str account_name: The name of the account.
        :param Api api: An instance of the Api class.
        """
        self.name = account_name
        self.api = api
        self._data = {}

    def refresh(self):
        """Fetch the account data from the blockchain."""
        if not self.api:
            raise ValueError("API not configured.")
        self._data = self.api.call("condenser_api", "get_accounts", [[self.name]])[0]

    def __getitem__(self, key):
        return self._data.get(key)

    def __str__(self):
        return f"<Account {self.name}>"
