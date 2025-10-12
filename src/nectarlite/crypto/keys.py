# -*- coding: utf-8 -*-

from ecdsa import SECP256k1, SigningKey, VerifyingKey


class PrivateKey:
    def __init__(self, wif):
        # The wif parameter is expected to be the raw private key in bytes
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
            # Handle string input by removing the prefix and converting to bytes
            if vk.startswith(prefix):
                vk = vk[len(prefix) :]
            self.vk = VerifyingKey.from_string(bytes.fromhex(vk), curve=SECP256k1)
        else:
            # This expects a string of bytes
            self.vk = VerifyingKey.from_string(vk, curve=SECP256k1)
        self.prefix = prefix

    def point(self):
        return self.vk.pubkey.point

    def __str__(self):
        # Return public key in a format that starts with the prefix
        return str(self.prefix) + str(self.vk.to_string("compressed").hex())
