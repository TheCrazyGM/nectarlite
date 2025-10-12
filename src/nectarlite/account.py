"""Account class for interacting with Hive accounts."""

from .amount import Amount


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

        # Properties that should be cast to Amount objects
        self._amount_fields = {
            "balance",
            "hbd_balance",
            "savings_balance",
            "savings_hbd_balance",
            "reward_hbd_balance",
            "reward_hive_balance",
            "reward_vesting_balance",
            "vesting_shares",
            "delegated_vesting_shares",
            "received_vesting_shares",
            "vesting_withdraw_rate",
        }

    def refresh(self):
        """Fetch the account data from the blockchain."""
        if not self.api:
            raise ValueError("API not configured.")

        accounts = self.api.call("condenser_api", "get_accounts", [[self.name]])
        if not accounts:
            raise ValueError(f"Account '{self.name}' not found.")
        self._data = accounts[0]

    def __getattr__(self, key):
        """Get an attribute from the account data, fetching if necessary."""
        # Avoid recursion on self._data
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
                # Value is a string like "1.234 HIVE"
                amount, asset = value.split()
                return Amount(float(amount), asset, api=self.api)
            except (ValueError, IndexError):
                # If splitting fails, it might not be a standard amount string.
                # e.g. vesting_withdraw_rate on a new account is '0.000000 VESTS'
                return value

        return value

    def __getitem__(self, key):
        """Allow dictionary-style access to the raw account data."""
        if not self._data:
            self.refresh()
        return self._data.get(key)

    def __str__(self):
        return f"<Account {self.name}>"
