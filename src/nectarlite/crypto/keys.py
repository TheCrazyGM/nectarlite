# -*- coding: utf-8 -*-

from ecdsa import SECP256k1, SigningKey, VerifyingKey

from .base58 import gph_base58_check_decode, gph_base58_check_encode


class PrivateKey:
    def __init__(self, wif):
        # Accept raw private key bytes or hex strings
        if isinstance(wif, str):
            wif = bytes.fromhex(wif)
        self.sk = SigningKey.from_string(wif, curve=SECP256k1)

    def __int__(self):
        return self.sk.privkey.secret_multiplier

    @property
    def pubkey(self):
        return PublicKey(self.sk.get_verifying_key())


class PublicKey:
    def __init__(self, vk, prefix="STM"):
        if isinstance(vk, VerifyingKey):
            self.vk = vk
        elif isinstance(vk, str):
            # Handle string input provided as Hive-style public key
            key_str = vk
            if key_str.startswith(prefix):
                key_str = key_str[len(prefix) :]

            try:
                key_hex = gph_base58_check_decode(key_str)
                key_bytes = bytes.fromhex(key_hex)
            except Exception:
                # Fallback for raw hex strings
                key_bytes = bytes.fromhex(key_str)

            self.vk = VerifyingKey.from_string(key_bytes, curve=SECP256k1)
        else:
            # This expects a string of bytes
            self.vk = VerifyingKey.from_string(vk, curve=SECP256k1)
        self.prefix = prefix

    def point(self):
        return self.vk.pubkey.point

    def to_compressed_bytes(self):
        return self.vk.to_string("compressed")

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        key_hex = self.to_compressed_bytes().hex()
        encoded = gph_base58_check_encode(key_hex)
        return f"{self.prefix}{encoded}"
