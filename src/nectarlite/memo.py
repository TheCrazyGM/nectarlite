# -*- coding: utf-8 -*-
import random

from .account import Account
from .crypto.keys import PublicKey
from .crypto.memo import decode_memo, encode_memo
from .exceptions import MissingKeyError


class Memo:
    """Deals with Memos that are attached to a transfer."""

    def __init__(self, from_account=None, to_account=None, wallet=None, api=None):
        self.api = api
        self.wallet = wallet
        self.from_account = from_account
        self.to_account = to_account

    def encrypt(self, memo_text):
        """Encrypt a memo"""
        if not memo_text:
            return None

        if not self.wallet:
            raise ValueError("Wallet not configured.")
        if not self.from_account or not self.to_account:
            raise ValueError("From and to accounts must be configured.")

        priv_key = self.wallet.get_private_key(self.from_account.name, "memo")
        if not priv_key:
            raise MissingKeyError(
                f"Memo key for {self.from_account.name} not found in wallet."
            )

        to_account_data = Account(self.to_account.name, api=self.api)
        to_pub_key_str = to_account_data.memo_key
        pub_key = PublicKey(to_pub_key_str)

        nonce = str(random.getrandbits(64))
        return encode_memo(priv_key, pub_key, nonce, memo_text)

    def decrypt(self, encrypted_memo):
        """Decrypt a memo"""
        if not encrypted_memo or not encrypted_memo.startswith("#"):
            return encrypted_memo

        if not self.wallet:
            raise ValueError("Wallet not configured.")

        # Scenario 1: We are the recipient
        try:
            priv_key = self.wallet.get_private_key(self.to_account.name, "memo")
            from_account_data = Account(self.from_account.name, api=self.api)
            pub_key = PublicKey(from_account_data.memo_key)
            if priv_key and pub_key:
                return decode_memo(priv_key, pub_key, encrypted_memo)
        except (ValueError, MissingKeyError):
            pass

        # Scenario 2: We are the sender
        try:
            priv_key = self.wallet.get_private_key(self.from_account.name, "memo")
            to_account_data = Account(self.to_account.name, api=self.api)
            pub_key = PublicKey(to_account_data.memo_key)
            if priv_key and pub_key:
                return decode_memo(priv_key, pub_key, encrypted_memo)
        except (ValueError, MissingKeyError):
            pass

        raise MissingKeyError("Could not decrypt memo with any of the available keys.")
