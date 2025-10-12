"""ECDSA signing and verification."""

import hashlib

import ecdsa

from ..exceptions import InvalidKeyFormatError
from .base58 import base58_check_decode, gph_base58_check_decode


def _wif_to_raw_private_key(wif: str) -> bytes:
    decoded_hex = base58_check_decode(wif, skip_first_byte=False)
    decoded_bytes = bytes.fromhex(decoded_hex)

    if len(decoded_bytes) not in (33, 34):
        raise InvalidKeyFormatError("Invalid WIF payload length.")

    # First byte is version/network prefix.
    raw_key = decoded_bytes[1:]

    # Optional compression flag at the end.
    if len(raw_key) == 33 and raw_key[-1] == 0x01:
        raw_key = raw_key[:-1]

    if len(raw_key) != 32:
        raise InvalidKeyFormatError("Invalid raw private key length.")

    return raw_key


def sign(message, wif):
    """Sign a message with a private key in WIF format."""
    if not isinstance(message, bytes):
        message = bytes(message, "utf-8")

    digest = hashlib.sha256(message).digest()

    try:
        signing_key = ecdsa.SigningKey.from_string(
            _wif_to_raw_private_key(wif), curve=ecdsa.SECP256k1
        )
    except Exception as exc:
        raise InvalidKeyFormatError(str(exc)) from exc

    order = ecdsa.SECP256k1.order

    def _is_canonical(sig_bytes: bytes) -> bool:
        sig = bytearray(sig_bytes)
        return (
            not (sig[0] & 0x80)
            and not (sig[0] == 0 and not (sig[1] & 0x80))
            and not (sig[32] & 0x80)
            and not (sig[32] == 0 and not (sig[33] & 0x80))
        )

    def _recover_public_key(digest_bytes: bytes, signature_bytes: bytes, rec_id: int):
        from ecdsa import ellipticcurve, numbertheory

        curve = ecdsa.SECP256k1.curve
        generator = ecdsa.SECP256k1.generator

        r, s = ecdsa.util.sigdecode_string(signature_bytes, order)
        x = r + (rec_id // 2) * order
        if x >= curve.p():
            return None

        alpha = (pow(x, 3, curve.p()) + curve.a() * x + curve.b()) % curve.p()
        try:
            beta = numbertheory.square_root_mod_prime(alpha, curve.p())
        except Exception:
            return None
        y = beta if ((beta - (rec_id % 2)) % 2 == 0) else (curve.p() - beta)

        R = ellipticcurve.Point(curve, x, y, order)
        if not order * R == ellipticcurve.INFINITY:
            return None

        e = ecdsa.util.string_to_number(digest_bytes)
        r_inv = numbertheory.inverse_mod(r, order)
        Q = r_inv * (s * R + (-e % order) * generator)
        return ecdsa.VerifyingKey.from_public_point(Q, curve=ecdsa.SECP256k1)

    def _find_recovery_id(digest_bytes: bytes, signature_bytes: bytes, vk):
        target = vk.to_string()
        for rec_id in range(4):
            candidate = _recover_public_key(digest_bytes, signature_bytes, rec_id)
            if candidate and candidate.to_string() == target:
                return rec_id
        return None

    while True:
        raw_sig = signing_key.sign_digest_deterministic(
            digest,
            hashfunc=hashlib.sha256,
            sigencode=ecdsa.util.sigencode_string,
        )
        r, s = ecdsa.util.sigdecode_string(raw_sig, order)
        if s > order // 2:
            s = order - s
        canonical_sig = ecdsa.util.sigencode_string(r, s, order)
        if not _is_canonical(canonical_sig):
            continue
        rec_id = _find_recovery_id(digest, canonical_sig, signing_key.get_verifying_key())
        if rec_id is None:
            continue
        compact = bytes([rec_id + 27 + 4]) + canonical_sig
        return compact


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
