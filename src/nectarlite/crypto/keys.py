# -*- coding: utf-8 -*-

from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

from .base58 import gph_base58_check_decode, gph_base58_check_encode


class PrivateKey:
    def __init__(self, key_bytes):
        if isinstance(key_bytes, str):
            key_bytes = bytes.fromhex(key_bytes)
        if not isinstance(key_bytes, (bytes, bytearray)) or len(key_bytes) != 32:
            raise ValueError("Private key must be 32 raw bytes")

        private_value = int.from_bytes(key_bytes, "big")
        self._key = ec.derive_private_key(private_value, ec.SECP256K1())

    def __int__(self):
        return self._key.private_numbers().private_value

    @property
    def key(self):
        return self._key

    @property
    def pubkey(self):
        return PublicKey(self._key.public_key())


class PublicKey:
    def __init__(self, key, prefix="STM"):
        if isinstance(key, ec.EllipticCurvePublicKey):
            self._key = key
        elif isinstance(key, (bytes, bytearray)):
            self._key = ec.EllipticCurvePublicKey.from_encoded_point(
                ec.SECP256K1(), key
            )
        elif isinstance(key, str):
            key_str = key
            if key_str.startswith(prefix):
                key_str = key_str[len(prefix) :]

            try:
                key_hex = gph_base58_check_decode(key_str)
                key_bytes = bytes.fromhex(key_hex)
            except Exception:
                key_bytes = bytes.fromhex(key_str)

            self._key = ec.EllipticCurvePublicKey.from_encoded_point(
                ec.SECP256K1(), key_bytes
            )
        else:
            raise TypeError("Unsupported public key input")

        self.prefix = prefix

    @property
    def key(self):
        return self._key

    def point(self):
        numbers = self._key.public_numbers()
        return numbers.x, numbers.y

    def to_compressed_bytes(self):
        return self._key.public_bytes(Encoding.X962, PublicFormat.CompressedPoint)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        key_hex = self.to_compressed_bytes().hex()
        encoded = gph_base58_check_encode(key_hex)
        return f"{self.prefix}{encoded}"
