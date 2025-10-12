"""BIP32 hierarchical deterministic keys."""

import hashlib
import hmac

import ecdsa

BIP32_HARDEN = 0x80000000


class BIP32Key:
    """BIP32 hierarchical deterministic keys."""

    def __init__(self, private_key, chain_code):
        self.private_key = private_key
        self.chain_code = chain_code

    @staticmethod
    def from_seed(seed):
        """Create a new BIP32 key from a seed."""
        i64 = hmac.new(b"Bitcoin seed", seed, hashlib.sha512).digest()
        return BIP32Key(i64[:32], i64[32:])

    def get_child_key(self, i):
        """Derive a child key."""
        if i & BIP32_HARDEN:
            data = b"\0" + self.private_key + i.to_bytes(4, "big")
        else:
            public_key = ecdsa.SigningKey.from_string(
                self.private_key, curve=ecdsa.SECP256k1
            ).get_verifying_key()
            data = public_key.to_string("compressed") + i.to_bytes(4, "big")

        i64 = hmac.new(self.chain_code, data, hashlib.sha512).digest()
        il, ir = i64[:32], i64[32:]

        il_int = int.from_bytes(il, "big")
        pvt_int = int.from_bytes(self.private_key, "big")
        k_int = (il_int + pvt_int) % ecdsa.SECP256k1.order

        return BIP32Key(k_int.to_bytes(32, "big"), ir)
