"""AES encryption and decryption for memos."""

import base64
import hashlib

from Cryptodome import Random
from Cryptodome.Cipher import AES


class AESCipher:
    """AES encryption and decryption for memos."""

    def __init__(self, key):
        self.bs = 32
        self.key = hashlib.sha256(key.encode("utf-8")).digest()

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(
            self.bs - len(s) % self.bs
        ).encode("utf-8")

    def _unpad(self, s):
        return s[: -ord(s[len(s) - 1 :])]

    def encrypt(self, raw):
        """Encrypt a memo."""
        raw = self._pad(raw.encode("utf-8"))
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw)).decode("utf-8")

    def decrypt(self, enc):
        """Decrypt a memo."""
        enc = base64.b64decode(enc)
        iv = enc[: AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size :])).decode("utf-8")
