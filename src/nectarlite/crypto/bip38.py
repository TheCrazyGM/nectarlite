"""BIP38 encrypted private keys."""

import hashlib
from binascii import hexlify, unhexlify

import ecdsa
import scrypt
from Cryptodome.Cipher import AES

from .base58 import gph_base58_check_decode, gph_base58_check_encode


def _encrypt_xor(a, b, aes):
    """Returns encrypt(a ^ b)."""
    a = unhexlify("%0.32x" % (int(a, 16) ^ int(hexlify(b), 16)))
    return aes.encrypt(a)


def encrypt(privkey_wif, passphrase):
    """Encrypt a private key in WIF format."""
    privkey_hex = gph_base58_check_decode(privkey_wif)
    # get address
    # this is a bit of a hack, but it works for now
    # I will need to implement a proper address generation function later
    pubkey = ecdsa.SigningKey.from_string(
        bytes.fromhex(privkey_hex), curve=ecdsa.SECP256k1
    ).get_verifying_key()
    address = "STM" + gph_base58_check_encode(
        hashlib.new(
            "ripemd160", hashlib.sha256(pubkey.to_string("compressed")).digest()
        ).digest()
    )

    salt = hashlib.sha256(hashlib.sha256(address.encode("utf-8")).digest()).digest()[:4]
    key = scrypt.hash(passphrase.encode("utf-8"), salt, 16384, 8, 8, 64)
    derived_half1, derived_half2 = (key[:32], key[32:])
    aes = AES.new(derived_half2, AES.MODE_ECB)
    encrypted_half1 = _encrypt_xor(privkey_hex[:32], derived_half1[:16], aes)
    encrypted_half2 = _encrypt_xor(privkey_hex[32:], derived_half1[16:], aes)
    payload = b"\x01\x42\xc0" + salt + encrypted_half1 + encrypted_half2
    checksum = hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]
    return gph_base58_check_encode(payload + checksum)


def decrypt(encrypted_privkey, passphrase):
    """Decrypt a BIP38 encrypted private key."""
    d = gph_base58_check_decode(encrypted_privkey)
    d = d[2:]  # remove trailing 0x01 and 0x42
    flagbyte = d[0:1]  # get flag byte
    d = d[1:]  # get payload
    if not flagbyte == b"\xc0":
        raise AssertionError("Flagbyte has to be 0xc0")
    salt = d[0:4]
    d = d[4:-4]
    key = scrypt.hash(passphrase.encode("utf-8"), salt, 16384, 8, 8, 64)
    derivedhalf1 = key[0:32]
    derivedhalf2 = key[32:64]
    encryptedhalf1 = d[0:16]
    encryptedhalf2 = d[16:32]
    aes = AES.new(derivedhalf2, AES.MODE_ECB)
    decryptedhalf2 = aes.decrypt(encryptedhalf2)
    decryptedhalf1 = aes.decrypt(encryptedhalf1)
    privraw = decryptedhalf1 + decryptedhalf2
    privraw = "%064x" % (int(hexlify(privraw), 16) ^ int(hexlify(derivedhalf1), 16))
    return gph_base58_check_encode("80" + privraw)
