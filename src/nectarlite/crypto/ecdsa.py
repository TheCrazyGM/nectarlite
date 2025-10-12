"""ECDSA signing and verification using cryptography and secp256k1 helpers."""

import hashlib

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import (
    decode_dss_signature,
    encode_dss_signature,
)
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

from ..exceptions import InvalidKeyFormatError
from .base58 import base58_check_decode, gph_base58_check_decode
from .keys import PrivateKey
from .secp256k1 import (
    G,
    N,
    P,
    compress_point,
    decompress_point,
    point_add,
    point_neg,
    scalar_mult,
)


def _wif_to_raw_private_key(wif: str) -> bytes:
    decoded_hex = base58_check_decode(wif, skip_first_byte=False)
    decoded_bytes = bytes.fromhex(decoded_hex)

    if len(decoded_bytes) not in (33, 34):
        raise InvalidKeyFormatError("Invalid WIF payload length.")

    raw_key = decoded_bytes[1:]

    if len(raw_key) == 33 and raw_key[-1] == 0x01:
        raw_key = raw_key[:-1]

    if len(raw_key) != 32:
        raise InvalidKeyFormatError("Invalid raw private key length.")

    return raw_key


def _recover_public_key(e: int, r: int, s: int, rec_id: int):
    x = r + (rec_id // 2) * N
    if x >= P:
        return None

    try:
        R = decompress_point(x, rec_id % 2)
    except ValueError:
        return None

    if scalar_mult(N, R) is not None:
        return None

    r_inv = pow(r, -1, N)

    sR = scalar_mult(s % N, R)
    eG = scalar_mult(e % N, G)
    combined = point_add(sR, point_neg(eG))
    if combined is None:
        return None
    Q = scalar_mult(r_inv % N, combined)
    if Q is None:
        return None

    try:
        compressed = compress_point(Q)
        return ec.EllipticCurvePublicKey.from_encoded_point(ec.SECP256K1(), compressed)
    except ValueError:
        return None


def sign(message, wif):
    """Sign a message with a private key in WIF format."""
    if not isinstance(message, bytes):
        message = bytes(message, "utf-8")

    digest = hashlib.sha256(message).digest()
    e = int.from_bytes(digest, "big") % N

    try:
        priv = PrivateKey(_wif_to_raw_private_key(wif))
    except Exception as exc:
        raise InvalidKeyFormatError(str(exc)) from exc

    der_signature = priv.key.sign(message, ec.ECDSA(hashes.SHA256()))
    r, s = decode_dss_signature(der_signature)

    if s > N // 2:
        s = N - s

    canonical = r.to_bytes(32, "big") + s.to_bytes(32, "big")

    pub_compressed = priv.pubkey.to_compressed_bytes()

    for rec_id in range(4):
        recovered = _recover_public_key(e, r, s, rec_id)
        if (
            recovered
            and recovered.public_bytes(Encoding.X962, PublicFormat.CompressedPoint)
            == pub_compressed
        ):
            return bytes([27 + 4 + rec_id]) + canonical

    raise InvalidKeyFormatError("Could not recover public key from signature")


def verify(message, signature, public_key):
    """Verify a signature with a public key."""
    if not isinstance(message, bytes):
        message = bytes(message, "utf-8")

    try:
        pub_hex = gph_base58_check_decode(public_key[3:])
        pub_bytes = bytes.fromhex(pub_hex)
        verifying_key = ec.EllipticCurvePublicKey.from_encoded_point(
            ec.SECP256K1(), pub_bytes
        )
    except Exception as exc:
        raise InvalidKeyFormatError(str(exc)) from exc

    if len(signature) != 65:
        raise InvalidKeyFormatError("Invalid signature length")

    r = int.from_bytes(signature[1:33], "big")
    s = int.from_bytes(signature[33:], "big")
    der = encode_dss_signature(r, s)

    try:
        verifying_key.verify(der, message, ec.ECDSA(hashes.SHA256()))
        return True
    except InvalidSignature:
        return False
