"""Account class for interacting with Hive accounts."""

from datetime import datetime, timezone

from .amount import Amount
from .exceptions import NodeError
from .haf import HAF
from .transaction import Follow, Transaction

VOTING_MANA_REGENERATION_SECONDS = 5 * 24 * 60 * 60
RC_MANA_REGENERATION_SECONDS = 5 * 24 * 60 * 60


def _parse_time(value):
    """Parse various timestamp formats into timezone-aware datetimes."""

    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)

    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value, tz=timezone.utc)

    if isinstance(value, str):
        cleaned = value.strip()
        if not cleaned:
            return None
        if cleaned.endswith("Z"):
            cleaned = f"{cleaned[:-1]}+00:00"
        try:
            return datetime.fromisoformat(cleaned)
        except ValueError:
            try:
                return datetime.strptime(cleaned, "%Y-%m-%dT%H:%M:%S").replace(
                    tzinfo=timezone.utc
                )
            except ValueError:
                return None

    return None


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
        self._rc_info = None

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
            Follow(follower=self.name, following=account_to_follow, what=["blog"])
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

    def get_voting_power(self, refresh=False):
        """Calculate the current voting power percentage.

        :param bool refresh: If True, force a data refresh from the API.
        :return: Voting power in percent (0-100).
        """

        if refresh or not self._data:
            if not self.api:
                raise ValueError("API not configured.")
            self.refresh()

        manabar = self._data.get("voting_manabar") or {}
        last_update = _parse_time(
            manabar.get("last_update_time") or self._data.get("last_vote_time")
        )

        try:
            current_mana = int(manabar.get("current_mana"))
        except (TypeError, ValueError):
            voting_power = self._data.get("voting_power")
            current_mana = int(voting_power) if voting_power is not None else 0

        try:
            max_mana = int(manabar.get("max_mana"))
        except (TypeError, ValueError):
            max_mana = 10000

        if last_update is not None:
            diff = (datetime.now(timezone.utc) - last_update).total_seconds()
            regenerated = diff * max_mana / VOTING_MANA_REGENERATION_SECONDS
            current_mana = min(max_mana, current_mana + regenerated)

        if max_mana <= 0:
            return 0.0

        return float(current_mana) / max_mana * 100

    @property
    def voting_power(self):
        """Current voting power percentage."""

        return self.get_voting_power()

    @property
    def vp(self):
        """Alias for :pyattr:`voting_power`."""

        return self.voting_power

    def get_rc_info(self, refresh=False):
        """Fetch and cache Resource Credit information.

        :param bool refresh: If True, force a fresh fetch even if cached.
        :return: Dict with RC metrics or ``None`` if unavailable.
        """

        if self._rc_info is not None and not refresh:
            return self._rc_info

        if not self.api:
            raise ValueError("API not configured.")

        try:
            response = self.api.call(
                "rc_api", "find_rc_accounts", {"accounts": [self.name]}
            )
        except NodeError:
            self._rc_info = None
            return None

        rc_accounts = None
        if isinstance(response, dict):
            rc_accounts = response.get("rc_accounts") or response.get("result")
        elif isinstance(response, list):
            rc_accounts = response

        if not rc_accounts:
            self._rc_info = None
            return None

        rc_account = rc_accounts[0]
        manabar = rc_account.get("rc_manabar", {})

        try:
            max_mana = int(rc_account.get("max_rc"))
        except (TypeError, ValueError):
            max_mana = 0

        try:
            last_mana = int(manabar.get("current_mana"))
        except (TypeError, ValueError):
            last_mana = 0

        last_update = _parse_time(manabar.get("last_update_time"))
        current_mana = last_mana
        if last_update is not None and max_mana:
            diff = (datetime.now(timezone.utc) - last_update).total_seconds()
            regenerated = diff * max_mana / RC_MANA_REGENERATION_SECONDS
            current_mana = min(max_mana, last_mana + regenerated)

        current_percent = (float(current_mana) / max_mana * 100) if max_mana else 0.0
        last_percent = (float(last_mana) / max_mana * 100) if max_mana else 0.0

        info = {
            "last_mana": last_mana,
            "current_mana": current_mana,
            "max_mana": max_mana,
            "last_update_time": last_update,
            "last_percent": last_percent,
            "current_percent": current_percent,
        }

        self._rc_info = info
        return info

    @property
    def rc_info(self):
        """Cached Resource Credit info."""

        return self.get_rc_info()

    @property
    def rc(self):
        """Current Resource Credit percentage."""

        info = self.get_rc_info()
        return info["current_percent"] if info is not None else None
