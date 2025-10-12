"""Base58 encoding and decoding."""

import hashlib
from binascii import hexlify, unhexlify

BASE58_ALPHABET = b"123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


def base58decode(base58_str):
    """Decode a Base58 encoded string."""
    base58_text = bytes(base58_str, "ascii")
    n = 0
    leading_zeroes_count = 0
    for b in base58_text:
        n = n * 58 + BASE58_ALPHABET.find(bytes([b]))
        if n == 0:
            leading_zeroes_count += 1
    res = bytearray()
    while n >= 256:
        div, mod = divmod(n, 256)
        res.insert(0, mod)
        n = div
    else:
        res.insert(0, n)
    return hexlify(bytearray(1) * leading_zeroes_count + res).decode("ascii")


def base58encode(hexstring):
    """Encode a hex string as Base58."""
    byteseq = bytes(unhexlify(bytes(hexstring, "ascii")))
    n = 0
    leading_zeroes_count = 0
    for c in byteseq:
        n = n * 256 + c
        if n == 0:
            leading_zeroes_count += 1
    res = bytearray()
    while n >= 58:
        div, mod = divmod(n, 58)
        res.insert(0, BASE58_ALPHABET[mod])
        n = div
    else:
        res.insert(0, BASE58_ALPHABET[n])
    return (BASE58_ALPHABET[0:1] * leading_zeroes_count + res).decode("ascii")


def ripemd160(data) -> bytes:
    """RIPEMD160 hash of raw bytes or hex string."""

    h = hashlib.new("ripemd160")
    if isinstance(data, str):
        h.update(unhexlify(data))
    else:
        h.update(data)
    return h.digest()


def doublesha256(s: str) -> bytes:
    """Double SHA256 hash of a hex string."""
    return hashlib.sha256(hashlib.sha256(unhexlify(s)).digest()).digest()


def gph_base58_check_encode(s: str) -> str:
    """Graphene-style Base58 check encoding from a hex string."""

    checksum = ripemd160(s)[:4]
    result_hex = s + hexlify(checksum).decode("ascii")
    return base58encode(result_hex)


def gph_base58_check_decode(s: str) -> str:
    """Graphene-style Base58 check decoding to a hex string."""
    decoded_hex = base58decode(s)
    decoded_bytes = unhexlify(decoded_hex)
    payload_hex = decoded_hex[:-8]
    original_checksum = decoded_bytes[-4:]

    calculated_checksum = ripemd160(payload_hex)[:4]

    if not (original_checksum == calculated_checksum):
        raise AssertionError("Invalid checksum")
    return payload_hex


def base58_check_decode(s: str, skip_first_byte: bool = True) -> str:
    """Bitcoin-style Base58 check decoding using double SHA256."""

    decoded_hex = base58decode(s)
    decoded_bytes = unhexlify(decoded_hex)
    payload_hex = decoded_hex[:-8]
    original_checksum = decoded_bytes[-4:]

    calculated_checksum = doublesha256(payload_hex)[:4]

    if not (original_checksum == calculated_checksum):
        raise AssertionError("Invalid checksum")

    if skip_first_byte:
        return payload_hex[2:]
    return payload_hex
