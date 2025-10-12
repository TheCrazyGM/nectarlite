"""Serialization types for Hive transactions."""

import struct
from datetime import datetime


def varint(n):
    """Varint encoding."""
    data = b""
    while n >= 0x80:
        data += bytes([(n & 0x7F) | 0x80])
        n >>= 7
    data += bytes([n])
    return data


def varintdecode(data):
    """Varint decoding."""
    shift = 0
    result = 0
    for b in bytes(data):
        result |= (b & 0x7F) << shift
        if not (b & 0x80):
            break
        shift += 7
    return result


class Varint:
    """Varint."""

    def __init__(self, d):
        self.data = int(d)

    def __bytes__(self):
        return varint(self.data)


class Uint8:
    """Uint8."""

    def __init__(self, d):
        self.data = int(d)

    def __bytes__(self):
        return struct.pack("<B", self.data)


class Uint16:
    """Uint16."""

    def __init__(self, d):
        self.data = int(d)

    def __bytes__(self):
        return struct.pack("<H", self.data)


class Uint32:
    """Uint32."""

    def __init__(self, d):
        self.data = int(d)

    def __bytes__(self):
        return struct.pack("<I", self.data)


class Int16:
    """Int16."""

    def __init__(self, d):
        self.data = int(d)

    def __bytes__(self):
        return struct.pack("<h", int(self.data))


class Int64:
    """Int64."""

    def __init__(self, d):
        self.data = int(d)

    def __bytes__(self):
        return struct.pack("<q", self.data)


class Uint64:
    """Uint64."""

    def __init__(self, d):
        self.data = int(d)

    def __bytes__(self):
        return struct.pack("<Q", self.data)


class String:
    """String."""

    def __init__(self, d):
        self.data = d

    def __bytes__(self):
        d = self.data.encode("utf-8")
        return varint(len(d)) + d


class Array:
    """Array."""

    def __init__(self, d):
        self.data = d

    def __bytes__(self):
        return varint(len(self.data)) + b"".join(bytes(item) for item in self.data)


class Bool:
    """Bool."""

    def __init__(self, d):
        self.data = bool(d)

    def __bytes__(self):
        return struct.pack("<?", self.data)


class PointInTime:
    """PointInTime."""

    def __init__(self, d):
        self.data = d

    def __bytes__(self):
        dt = datetime.strptime(self.data, "%Y-%m-%dT%H:%M:%S")
        return struct.pack("<I", int(dt.timestamp()))


class Optional:
    """Optional."""

    def __init__(self, d):
        self.data = d

    def __bytes__(self):
        if self.data is None:
            return b"\x00"
        else:
            return b"\x01" + bytes(self.data)
