from typing import Dict, Optional

from .crypto.base58 import base58_check_decode
from .crypto.keys import PrivateKey
from .exceptions import InvalidKeyFormatError, MissingKeyError
from .transaction import Transaction


class Wallet:
    """Simple in-memory wallet for managing Hive private keys by account and role."""

    def __init__(self) -> None:
        self._keys: Dict[str, Dict[str, str]] = {}

    def add_key(self, account: str, role: str, wif: str) -> None:
        """Add a private key for an account role."""
        if role not in ("posting", "active", "memo"):
            raise ValueError("Role must be 'posting', 'active', or 'memo'.")
        if not isinstance(account, str) or not account:
            raise ValueError("Account must be a non-empty string.")
        if not wif.startswith("5"):
            raise InvalidKeyFormatError("Private WIF keys start with '5'.")

        try:
            decoded_hex = base58_check_decode(wif, skip_first_byte=False)
            decoded_bytes = bytes.fromhex(decoded_hex)
            if len(decoded_bytes) not in (33, 34):
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

    def get_private_key(self, account: str, role: str) -> Optional[PrivateKey]:
        """Get a PrivateKey object for the account/role."""
        wif = self.get_key(account, role)
        if wif is None:
            return None

        decoded_hex = base58_check_decode(wif, skip_first_byte=False)
        decoded_bytes = bytes.fromhex(decoded_hex)

        if len(decoded_bytes) not in (33, 34):
            raise InvalidKeyFormatError("Invalid WIF payload length.")

        # Drop the leading network/version byte.
        raw_key = decoded_bytes[1:]

        # Remove optional compression flag if present.
        if len(raw_key) == 33 and raw_key[-1] == 0x01:
            raw_key = raw_key[:-1]

        if len(raw_key) != 32:
            raise InvalidKeyFormatError("Invalid raw private key length.")

        return PrivateKey(raw_key)

    def sign(self, transaction: Transaction, account: str, role: str) -> None:
        """Sign the transaction using the specified account's role key."""
        wif = self.get_key(account, role)
        if wif is None:
            raise MissingKeyError(f"No {role} key for account '{account}'")
        transaction.sign(wif)
