# -*- coding: utf-8 -*-
import hashlib
from binascii import hexlify, unhexlify

from Crypto.Cipher import AES

from nectarlite.crypto.base58 import base58decode, base58encode


def get_shared_secret(priv, pub):
    """Generate a shared secret from a private key and a public key."""
    pub_point = pub.point()
    priv_point = int(priv)
    res = pub_point * priv_point
    res_hex = f"{res.x():x}"
    res_hex = "0" * (64 - len(res_hex)) + res_hex
    return hashlib.sha512(unhexlify(res_hex)).digest()


def encode_memo(priv, pub, nonce, message):
    """Encode a memo"""
    shared_secret = get_shared_secret(priv, pub)
    aes = AES.new(shared_secret[:32], AES.MODE_CBC, iv=shared_secret[32:48])

    # Checksum
    check = hashlib.sha256(shared_secret).digest()[:4]

    # Nonce
    nonce_bytes = int(nonce).to_bytes(8, "little")
    msg = nonce_bytes + check + message.encode("utf-8")

    # Padding
    pad = len(msg) % 16
    if pad:
        msg += b"\x00" * (16 - pad)

    encrypted = aes.encrypt(msg)
    return "#" + base58encode(hexlify(encrypted).decode("ascii"))


def decode_memo(priv, pub, encrypted_memo):
    """Decode a memo"""
    if not encrypted_memo.startswith("#"):
        return encrypted_memo

    encrypted = unhexlify(base58decode(encrypted_memo[1:]))

    shared_secret = get_shared_secret(priv, pub)
    aes = AES.new(shared_secret[:32], AES.MODE_CBC, iv=shared_secret[32:48])

    decrypted = aes.decrypt(encrypted)

    check_from_msg = decrypted[8:12]
    check_verify = hashlib.sha256(shared_secret).digest()[:4]

    if check_from_msg != check_verify:
        raise ValueError("Invalid checksum")

    return decrypted[12:].strip(b"\x00").decode("utf-8")
