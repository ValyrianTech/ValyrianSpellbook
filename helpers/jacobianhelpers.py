#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Elliptic curve parameters (secp256k1)

P = 2**256 - 2**32 - 977
N = 115792089237316195423570985008687907852837564279074904382605163141518161494337
A = 0
B = 7
Gx = 55066263022277343669578718895168534326250603453777594175500187360389116729240
Gy = 32670510020758816978083085130507043184471273380659243275938904335757337482424
G = (Gx, Gy)


def fast_add(a, b):
    return from_jacobian(jacobian_add(to_jacobian(a), to_jacobian(b)))


def fast_multiply(a, n):
    return from_jacobian(jacobian_multiply(to_jacobian(a), n))


def from_jacobian(p):
    z = inv(p[2], P)
    return (p[0] * z ** 2) % P, (p[1] * z ** 3) % P


def to_jacobian(p):
    o = (p[0], p[1], 1)
    return o


def jacobian_add(p, q):
    if not p[1]:
        return q
    if not q[1]:
        return p
    u1 = (p[0] * q[2] ** 2) % P
    u2 = (q[0] * p[2] ** 2) % P
    s1 = (p[1] * q[2] ** 3) % P
    s2 = (q[1] * p[2] ** 3) % P
    if u1 == u2:
        if s1 != s2:
            return 0, 0, 1
        return jacobian_double(p)
    h = u2 - u1
    r = s2 - s1
    h2 = (h * h) % P
    h3 = (h * h2) % P
    u1_h2 = (u1 * h2) % P
    nx = (r ** 2 - h3 - 2 * u1_h2) % P
    ny = (r * (u1_h2 - nx) - s1 * h3) % P
    nz = (h * p[2] * q[2]) % P
    return nx, ny, nz


def jacobian_multiply(a, n):
    if a[1] == 0 or n == 0:
        return 0, 0, 1
    if n == 1:
        return a
    if n < 0 or n >= N:
        return jacobian_multiply(a, n % N)
    if (n % 2) == 0:
        return jacobian_double(jacobian_multiply(a, n//2))
    if (n % 2) == 1:
        return jacobian_add(jacobian_double(jacobian_multiply(a, n//2)), a)


def jacobian_double(p):
    if not p[1]:
        return 0, 0, 0
    ysq = (p[1] ** 2) % P
    s = (4 * p[0] * ysq) % P
    m = (3 * p[0] ** 2 + A * p[2] ** 4) % P
    nx = (m**2 - 2 * s) % P
    ny = (m * (s - nx) - 8 * ysq ** 2) % P
    nz = (2 * p[1] * p[2]) % P
    return nx, ny, nz


def inv(a, n):
    if a == 0:
        return 0
    lm, hm = 1, 0
    low, high = a % n, n
    while low > 1:
        r = high//low
        nm, new = hm-lm*r, high-low*r
        lm, low, hm, high = nm, new, lm, low
    return lm % n
