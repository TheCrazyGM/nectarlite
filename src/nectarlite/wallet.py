from typing import Dict, Optional

from .crypto.base58 import gph_base58_check_decode
from .exceptions import InvalidKeyFormatError, MissingKeyError
from .transaction import Transaction


class Wallet:
    """Simple in-memory wallet for managing Hive private keys by account and role."""

    def __init__(self) -> None:
        self._keys: Dict[str, Dict[str, str]] = {}

    def add_key(self, account: str, role: str, wif: str) -> None:
        """Add a private key for an account role.

        Args:
            account: Account name (e.g., "yourusername").
            role: One of 'posting', 'active', or 'memo'.
            wif: WIF private key string (starts with '5').

        Raises:
            ValueError: Invalid account, role, or format.
            InvalidKeyFormatError: Malformed WIF.
        """
        if role not in ("posting", "active", "memo"):
            raise ValueError("Role must be 'posting', 'active', or 'memo'.")
        if not isinstance(account, str) or not account:
            raise ValueError("Account must be a non-empty string.")
        if not wif.startswith("5"):
            raise InvalidKeyFormatError("Private WIF keys start with '5'.")

        try:
            decoded = gph_base58_check_decode(wif)
            if len(decoded) < 32:  # Basic payload check
                raise InvalidKeyFormatError("Invalid WIF payload length.")
        except Exception:
            raise InvalidKeyFormatError("Invalid WIF format.")

        if account not in self._keys:
            self._keys[account] = {}
        self._keys[account][role] = wif

    def has_key(self, account: str, role: str) -> bool:
        """Check if a key is loaded for the account/role."""
        return account in self._keys and role in self._keys[account]

    def get_key(self, account: str, role: str) -> Optional[str]:
        """Get WIF key if available."""
        if self.has_key(account, role):
            return self._keys[account][role]
        return None

    def sign(self, transaction: Transaction, account: str, role: str) -> None:
        """Sign the transaction using the specified account's role key.

        Args:
            transaction: The Transaction to sign.
            account: Account name.
            role: Role to use ('posting', 'active', or 'memo').

        Raises:
            MissingKeyError: If no key for account/role.
        """
        wif = self.get_key(account, role)
        if wif is None:
            raise MissingKeyError(f"No {role} key for account '{account}'")
        transaction.sign(wif)
