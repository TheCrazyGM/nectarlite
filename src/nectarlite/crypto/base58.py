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


def ripemd160(s):
    """RIPEMD160 hash."""
    ripemd160 = hashlib.new("ripemd160")
    ripemd160.update(unhexlify(s))
    return ripemd160.digest()


def doublesha256(s):
    """Double SHA256 hash."""
    return hashlib.sha256(hashlib.sha256(unhexlify(s)).digest()).digest()


def gph_base58_check_encode(s):
    """Graphene-style Base58 check encoding."""
    checksum = ripemd160(s)[:4]
    result = s + hexlify(checksum).decode("ascii")
    return base58encode(result)


def gph_base58_check_decode(s):
    """Graphene-style Base58 check decoding."""
    s = unhexlify(base58decode(s))
    dec = hexlify(s[:-4]).decode("ascii")
    checksum = ripemd160(dec)[:4]
    if not (s[-4:] == checksum):
        raise AssertionError("Invalid checksum")
    return dec
