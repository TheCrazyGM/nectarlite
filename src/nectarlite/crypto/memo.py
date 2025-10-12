# -*- coding: utf-8 -*-
import hashlib
import struct
from binascii import hexlify, unhexlify

from Crypto.Cipher import AES

from nectarlite.crypto.base58 import base58decode, base58encode
from nectarlite.crypto.keys import PrivateKey, PublicKey
from nectarlite.crypto.secp256k1 import scalar_mult
from nectarlite.types import varint


def _read_varint(data):
    result = 0
    shift = 0
    length = 0
    for byte in data:
        byte_val = byte
        result |= (byte_val & 0x7F) << shift
        length += 1
        if not (byte_val & 0x80):
            break
        shift += 7
    return result, length


def _pad(data, block_size=16):
    pad_len = block_size - (len(data) % block_size)
    return data + bytes([pad_len]) * pad_len


def _unpad(data):
    pad_len = data[-1]
    if pad_len < 1 or pad_len > 16:
        raise ValueError("Invalid padding")
    if data[-pad_len:] != bytes([pad_len]) * pad_len:
        raise ValueError("Invalid padding")
    return data[:-pad_len]


def get_shared_secret(priv, pub):
    """Generate a shared secret from a private key and a public key."""
    if isinstance(priv, PrivateKey):
        priv_scalar = int(priv)
    else:
        priv_scalar = int(priv)

    pub_point = pub.point()
    shared_point = scalar_mult(priv_scalar, pub_point)
    if shared_point is None:
        raise ValueError("Invalid shared secret point")
    res_hex = f"{shared_point[0]:064x}"
    return res_hex


def _init_aes(shared_secret_hex, nonce):
    shared_secret = hashlib.sha512(unhexlify(shared_secret_hex)).hexdigest()
    ss = unhexlify(shared_secret)
    nonce_bytes = struct.pack("<Q", int(nonce))
    encryption_key = hashlib.sha512(nonce_bytes + ss).hexdigest()
    key = unhexlify(encryption_key[0:64])
    iv = unhexlify(encryption_key[64:96])
    check = struct.unpack_from("<I", hashlib.sha256(unhexlify(encryption_key)).digest())[0]
    return AES.new(key, AES.MODE_CBC, iv), check


def _serialize_memo(from_pub, to_pub, nonce, check, cipher_hex):
    from_bytes = from_pub.to_compressed_bytes()
    to_bytes = to_pub.to_compressed_bytes()
    nonce_bytes = struct.pack("<Q", int(nonce))
    check_bytes = struct.pack("<I", int(check))
    cipher_bytes = bytes.fromhex(cipher_hex)
    return (
        from_bytes
        + to_bytes
        + nonce_bytes
        + check_bytes
        + varint(len(cipher_bytes))
        + cipher_bytes
    )


def encode_memo(priv, pub, nonce, message, prefix="STM"):
    """Encode a memo compatible with Hive wire format."""
    shared_secret = get_shared_secret(priv, pub)
    aes, check = _init_aes(shared_secret, nonce)
    padded = _pad(message.encode("utf-8"))
    cipher_hex = hexlify(aes.encrypt(padded)).decode("ascii")

    memo_bytes = _serialize_memo(priv.pubkey, pub, nonce, check, cipher_hex)
    return "#" + base58encode(hexlify(memo_bytes).decode("ascii"))


def _deserialize_memo(raw_bytes):
    offset = 0
    from_bytes = raw_bytes[offset : offset + 33]
    offset += 33
    to_bytes = raw_bytes[offset : offset + 33]
    offset += 33
    nonce = struct.unpack_from("<Q", raw_bytes, offset)[0]
    offset += 8
    check = struct.unpack_from("<I", raw_bytes, offset)[0]
    offset += 4
    encrypted_len, consumed = _read_varint(raw_bytes[offset:])
    offset += consumed
    cipher_bytes = raw_bytes[offset : offset + encrypted_len]
    return from_bytes, to_bytes, nonce, check, cipher_bytes


def decode_memo(priv, pub, encrypted_memo, prefix="STM"):
    """Decode a memo encoded with Hive wire format."""
    if not encrypted_memo or not encrypted_memo.startswith("#"):
        return encrypted_memo

    raw_hex = base58decode(encrypted_memo[1:])
    raw_bytes = bytes.fromhex(raw_hex)
    from_bytes, to_bytes, nonce, check, cipher_bytes = _deserialize_memo(raw_bytes)

    priv_bytes = priv.pubkey.to_compressed_bytes()
    if priv_bytes == to_bytes:
        other_pub = PublicKey(from_bytes, prefix=prefix)
    elif priv_bytes == from_bytes:
        other_pub = PublicKey(to_bytes, prefix=prefix)
    elif pub is not None:
        other_pub = pub
    else:
        raise ValueError("Private key does not match memo participants")

    shared_secret = get_shared_secret(priv, other_pub)
    aes, checksum = _init_aes(shared_secret, nonce)
    if check != checksum:
        raise ValueError("Checksum failure")

    decrypted = aes.decrypt(cipher_bytes)
    message = _unpad(decrypted).decode("utf-8")
    return message
