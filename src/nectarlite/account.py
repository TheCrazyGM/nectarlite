"""Account class for interacting with Hive accounts."""

from .amount import Amount
from .haf import HAF
from .transaction import Follow, Transaction

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
        self._reputation = None

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
        
    def follow(self, account_to_follow):
        """Follow another account.
        
        :param str account_to_follow: The name of the account to follow.
        :raises ValueError: If API not configured or account not found.
        :return: The transaction response.
        :rtype: dict
        """
        if not self.api:
            raise ValueError("API not configured.")

        tx = Transaction(api=self.api)
        tx.append_op(
            Follow(
                follower=self.name,
                following=account_to_follow,
                what=["blog"]
            )
        )
        # Note: This requires the active key to be added to a wallet or passed directly
        # when calling tx.sign(wif)
        return tx
    
    def unfollow(self, account_to_unfollow):
        """Unfollow an account you are currently following.
        
        :param str account_to_unfollow: The name of the account to unfollow.
        :raises ValueError: If API not configured or account not found.
        :return: The transaction response.
        :rtype: dict
        """
        if not self.api:
            raise ValueError("API not configured.")

        tx = Transaction(api=self.api)
        tx.append_op(
            Follow(
                follower=self.name,
                following=account_to_unfollow,
                what=[],  # Empty list means unfollow
            )
        )
        return tx
    
    def ignore(self, account_to_ignore):
        """Mute/ignore another account.
        
        :param str account_to_ignore: The name of the account to ignore.
        :raises ValueError: If API not configured or account not found.
        :return: The transaction response.
        :rtype: dict
        """
        if not self.api:
            raise ValueError("API not configured.")

        tx = Transaction(api=self.api)
        tx.append_op(
            Follow(
                follower=self.name,
                following=account_to_ignore,
                what=["ignore"],  # "ignore" value means mute the account
            )
        )
        return tx
    
    def unignore(self, account_to_unignore):
        """Unmute an account you are currently ignoring.
        
        :param str account_to_unignore: The name of the account to unignore.
        :raises ValueError: If API not configured or account not found.
        :return: The transaction response.
        :rtype: dict
        """
        # Unignore is the same as unfollow in the Hive blockchain
        return self.unfollow(account_to_unignore)

    def get_reputation(self, haf_client=None, refresh=False):
        """Return the account reputation fetched from the HAF API.

        :param HAF haf_client: Optional pre-configured HAF client to use.
        :param bool refresh: If True, force a fresh fetch even if cached.
        :return: The raw reputation value or ``None`` if unavailable.
        """

        if self._reputation is not None and not refresh:
            return self._reputation

        client = haf_client or HAF()
        response = client.reputation(self.name)

        if isinstance(response, dict):
            reputation_value = response.get("reputation")
        elif isinstance(response, (int, float)):
            reputation_value = response
        else:
            reputation_value = None

        self._reputation = reputation_value
        return self._reputation

    @property
    def reputation(self):
        """Cached reputation property."""

        return self.get_reputation()

    @property
    def rep(self):
        """Alias for :pyattr:`reputation`."""

        return self.reputation
