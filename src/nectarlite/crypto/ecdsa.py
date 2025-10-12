"""ECDSA signing and verification."""

import hashlib

import ecdsa

from ..exceptions import InvalidKeyFormatError
from .base58 import gph_base58_check_decode


def sign(message, wif):
    """Sign a message with a private key in WIF format."""
    try:
        private_key_hex = gph_base58_check_decode(wif)
        signing_key = ecdsa.SigningKey.from_string(
            bytes.fromhex(private_key_hex), curve=ecdsa.SECP256k1
        )
        return signing_key.sign_digest_deterministic(
            hashlib.sha256(message).digest(),
            hashfunc=hashlib.sha256,
            sigencode=ecdsa.util.sigencode_string,
        )
    except Exception as e:
        raise InvalidKeyFormatError(str(e))


def verify(message, signature, public_key):
    """Verify a signature with a public key."""
    try:
        public_key_hex = gph_base58_check_decode(public_key[3:])
        verifying_key = ecdsa.VerifyingKey.from_string(
            bytes.fromhex(public_key_hex), curve=ecdsa.SECP256k1
        )
        return verifying_key.verify_digest(
            signature,
            hashlib.sha256(message).digest(),
            sigdecode=ecdsa.util.sigdecode_string,
        )
    except Exception as e:
        raise InvalidKeyFormatError(str(e))
