# -*- coding: utf-8 -*-
"""Lightweight secp256k1 helper utilities for scalar and point math."""

P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
A = 0
B = 7
Gx = 55066263022277343669578718895168534326250603453777594175500187360389116729240
Gy = 32670510020758816978083085130507043184471273380659243275938904335757337482424
G = (Gx, Gy)


def mod_inv(value: int, modulo: int) -> int:
    """Modular inverse using Fermat's little theorem (modulo must be prime)."""
    return pow(value, -1, modulo)


def is_on_curve(point):
    if point is None:
        return True
    x, y = point
    return (y * y - (x * x * x + A * x + B)) % P == 0


def point_add(p1, p2):
    if p1 is None:
        return p2
    if p2 is None:
        return p1

    x1, y1 = p1
    x2, y2 = p2

    if x1 == x2 and (y1 + y2) % P == 0:
        return None

    if p1 == p2:
        return point_double(p1)

    slope = ((y2 - y1) * mod_inv((x2 - x1) % P, P)) % P
    x3 = (slope * slope - x1 - x2) % P
    y3 = (slope * (x1 - x3) - y1) % P
    return x3, y3


def point_double(point):
    if point is None:
        return None
    x, y = point
    if y == 0:
        return None
    slope = ((3 * x * x + A) * mod_inv((2 * y) % P, P)) % P
    x3 = (slope * slope - 2 * x) % P
    y3 = (slope * (x - x3) - y) % P
    return x3, y3


def point_neg(point):
    if point is None:
        return None
    x, y = point
    return x, (-y) % P


def scalar_mult(k: int, point):
    if point is None or k % N == 0:
        return None
    if k < 0:
        return scalar_mult(-k, (point[0], (-point[1]) % P))

    result = None
    addend = point

    while k:
        if k & 1:
            result = point_add(result, addend)
        addend = point_double(addend)
        k >>= 1
    return result


def compress_point(point):
    if point is None:
        raise ValueError("Cannot compress point at infinity")
    x, y = point
    return bytes([2 + (y & 1)]) + x.to_bytes(32, "big")


def decompress_point(x: int, parity: int):
    if x >= P:
        raise ValueError("x coordinate out of range")
    alpha = (pow(x, 3, P) + B) % P
    beta = pow(alpha, (P + 1) // 4, P)
    if (beta & 1) != parity:
        beta = (-beta) % P
    point = (x, beta)
    if not is_on_curve(point):
        raise ValueError("Point not on curve")
    return point


def scalar_base_mult(k: int):
    return scalar_mult(k, G)
