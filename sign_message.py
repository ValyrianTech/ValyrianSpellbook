#!/usr/bin/env python

# the code below is 'borrowed' almost verbatim from electrum,
# https://gitorious.org/electrum/electrum
# and is under the GPLv3.

import ecdsa
import base64
import hashlib
from ecdsa.util import string_to_number

# secp256k1, http://www.oid-info.com/get/1.3.132.0.10
_p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
_r = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
_b = 0x0000000000000000000000000000000000000000000000000000000000000007
_a = 0x0000000000000000000000000000000000000000000000000000000000000000
_Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
_Gy = 0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8
curve_secp256k1 = ecdsa.ellipticcurve.CurveFp(_p, _a, _b)
generator_secp256k1 = ecdsa.ellipticcurve.Point(curve_secp256k1, _Gx, _Gy, _r)
oid_secp256k1 = (1, 3, 132, 0, 10)
SECP256k1 = ecdsa.curves.Curve("SECP256k1", curve_secp256k1, generator_secp256k1, oid_secp256k1)

addrtype = 0  # 0 for mainnet addresses, 111 for testnet addresses


# from http://eli.thegreenplace.net/2009/03/07/computing-modular-square-roots-in-python/

def modular_sqrt(a, p):
    """ Find a quadratic residue (mod p) of 'a'. p
    must be an odd prime.

    Solve the congruence of the form:
    x^2 = a (mod p)
    And returns x. Note that p - x is also a root.

    0 is returned is no square root exists for
    these a and p.

    The Tonelli-Shanks algorithm is used (except
    for some simple cases in which the solution
    is known from an identity). This algorithm
    runs in polynomial time (unless the
    generalized Riemann hypothesis is false).
    """
    # Simple cases
    #
    if legendre_symbol(a, p) != 1:
        return 0
    elif a == 0:
        return 0
    elif p == 2:
        return p
    elif p % 4 == 3:
        return pow(a, (p + 1) / 4, p)

    # Partition p-1 to s * 2^e for an odd s (i.e.
    # reduce all the powers of 2 from p-1)
    #
    s = p - 1
    e = 0
    while s % 2 == 0:
        s /= 2
        e += 1

    # Find some 'n' with a legendre symbol n|p = -1.
    # Shouldn't take long.
    #
    n = 2
    while legendre_symbol(n, p) != -1:
        n += 1

    # Here be dragons!
    # Read the paper "Square roots from 1; 24, 51,
    # 10 to Dan Shanks" by Ezra Brown for more
    # information
    #

    # x is a guess of the square root that gets better
    # with each iteration.
    # b is the "fudge factor" - by how much we're off
    # with the guess. The invariant x^2 = ab (mod p)
    # is maintained throughout the loop.
    # g is used for successive powers of n to update
    # both a and b
    # r is the exponent - decreases with each update
    #
    x = pow(a, (s + 1) / 2, p)
    b = pow(a, s, p)
    g = pow(n, s, p)
    r = e

    while True:
        t = b
        m = 0
        for m in xrange(r):
            if t == 1:
                break
            t = pow(t, 2, p)

        if m == 0:
            return x

        gs = pow(g, 2 ** (r - m - 1), p)
        g = (gs * gs) % p
        x = (x * gs) % p
        b = (b * g) % p
        r = m


def legendre_symbol(a, p):
    """ Compute the Legendre symbol a|p using
    Euler's criterion. p is a prime, a is
    relatively prime to p (if p divides
    a, then a|p = 0)

    Returns 1 if a has a square root modulo
    p, -1 otherwise.
    """
    ls = pow(a, (p - 1) / 2, p)
    return -1 if ls == p - 1 else ls


__b58chars = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
__b58base = len(__b58chars)


def b58encode(v):
    """ encode v, which is a string of bytes, to base58.
    """

    long_value = 0
    for (i, c) in enumerate(v[::-1]):
        long_value += (256 ** i) * ord(c)

    result = ''
    while long_value >= __b58base:
        div, mod = divmod(long_value, __b58base)
        result = __b58chars[mod] + result
        long_value = div
    result = __b58chars[long_value] + result

    # Bitcoin does a little leading-zero-compression:
    # leading 0-bytes in the input become leading-1s
    nPad = 0
    for c in v:
        if c == '\0':
            nPad += 1
        else:
            break

    return (__b58chars[0] * nPad) + result


def b58decode(v, length):
    """ decode v into a string of len bytes."""
    long_value = 0
    for (i, c) in enumerate(v[::-1]):
        long_value += __b58chars.find(c) * (__b58base ** i)

    result = ''
    while long_value >= 256:
        div, mod = divmod(long_value, 256)
        result = chr(mod) + result
        long_value = div
    result = chr(long_value) + result

    nPad = 0
    for c in v:
        if c == __b58chars[0]:
            nPad += 1
        else:
            break

    result = chr(0) * nPad + result
    if length is not None and len(result) != length:
        return None

    return result


def msg_magic(message):
    return "\x18Bitcoin Signed Message:\n" + chr(len(message)) + message


def double_sha256_hash(data):
    return hashlib.sha256(hashlib.sha256(data).digest()).digest()


def hash_160(public_key):
    md = hashlib.new('ripemd160')
    md.update(hashlib.sha256(public_key).digest())
    return md.digest()


def hash_160_to_bc_address(h160):
    vh160 = chr(addrtype) + h160
    h = double_sha256_hash(vh160)
    addr = vh160 + h[0:4]
    return b58encode(addr)


def public_key_to_bc_address(public_key):
    h160 = hash_160(public_key)
    return hash_160_to_bc_address(h160)


def encode_point(pubkey, compressed=False):
    order = generator_secp256k1.order()
    p = pubkey.pubkey.point
    x_str = ecdsa.util.number_to_string(p.x(), order)
    y_str = ecdsa.util.number_to_string(p.y(), order)
    if compressed:
        return chr(2 + (p.y() & 1)) + x_str
    else:
        return chr(4) + x_str + y_str


def verify_message(address, signature, message):
    """ See http://www.secg.org/download/aid-780/sec1-v2.pdf for the math
    Verify that a messege is signed by the private key of the given address

    :param address: The bitcoin address that signed the message
    :param signature: The signature
    :param message: The message
    :return: True or False
    """
    from ecdsa import numbertheory, ellipticcurve, util

    global addrtype
    if address[0] in ['1', '3']:
        # address is a mainnet address
        addrtype = 0
    elif address[0] in ['n', 'm', '2']:
        # address is a testnet address
        addrtype = 111

    curve = curve_secp256k1
    G = generator_secp256k1
    order = G.order()
    # extract r,s from signature
    sig = base64.b64decode(signature)
    if len(sig) != 65:
        raise BaseException("Wrong encoding")

    r, s = util.sigdecode_string(sig[1:], order)
    nV = ord(sig[0])
    if nV < 27 or nV >= 35:
        return False
    if nV >= 31:
        compressed = True
        nV -= 4
    else:
        compressed = False
    recid = nV - 27
    # 1.1
    x = r + (recid / 2) * order
    # 1.3
    alpha = (x * x * x + curve.a() * x + curve.b()) % curve.p()
    beta = modular_sqrt(alpha, curve.p())
    y = beta if (beta - recid) % 2 == 0 else curve.p() - beta
    # 1.4 the constructor checks that nR is at infinity
    R = ellipticcurve.Point(curve, x, y, order)
    # 1.5 compute e from message:
    h = double_sha256_hash(msg_magic(message))
    e = string_to_number(h)
    minus_e = -e % order
    # 1.6 compute Q = r^-1 (sR - eG)
    inv_r = numbertheory.inverse_mod(r, order)
    Q = inv_r * (s * R + minus_e * G)
    public_key = ecdsa.VerifyingKey.from_public_point(Q, curve=SECP256k1)
    # check that Q is the public key
    public_key.verify_digest(sig[1:], h, sigdecode=ecdsa.util.sigdecode_string)
    # check that we get the original signing address
    addr = public_key_to_bc_address(encode_point(public_key, compressed))

    return address == addr


def sign_message_with_secret(secret, message, compressed=False):
    private_key = ecdsa.SigningKey.from_secret_exponent(secret, curve=SECP256k1)

    public_key = private_key.get_verifying_key()
    signature = private_key.sign_digest(double_sha256_hash(msg_magic(message)), sigencode=ecdsa.util.sigencode_string)
    address = public_key_to_bc_address(encode_point(public_key, compressed))

    assert public_key.verify_digest(signature, double_sha256_hash(msg_magic(message)), sigdecode=ecdsa.util.sigdecode_string)
    for i in range(4):
        nV = 27 + i
        if compressed:
            nV += 4
        sig = base64.b64encode(chr(nV) + signature)
        try:
            if verify_message(address, sig, message):
                return sig
        except:
            continue
    else:
        raise BaseException("error: cannot sign message")


def sign_message_with_private_key(private_key, message):
    encoded_priv_key_bytes = b58decode(private_key, None)
    encoded_priv_key_hex_string = encoded_priv_key_bytes.encode('hex')

    compressed = is_compressed(private_key)
    if compressed:
        assert len(encoded_priv_key_hex_string) == 76
        # strip leading 0x08, 0x01 compressed flag, checksum
        secret_hex_string = encoded_priv_key_hex_string[2:-10]
    else:
        assert len(encoded_priv_key_hex_string) == 74
        # strip leading 0x08 and checksum
        secret_hex_string = encoded_priv_key_hex_string[2:-8]

    secret = int(secret_hex_string, 16)

    checksum = double_sha256_hash(encoded_priv_key_bytes[:-4])[:4].encode('hex')
    assert checksum == encoded_priv_key_hex_string[-8:]  # make sure private key is valid

    return sign_message_with_secret(secret, message, compressed)


def sign_and_verify(private_key, message, address):
    sig = sign_message_with_private_key(private_key, message)
    assert verify_message(address, sig, message)

    return sig


def sign_message(address, message, private_key):
    """
    Sign a message with the private key of an address

    :param address: A Bitcoin address
    :param message: The message to sign
    :param private_key: The private key of the address
    :return: The signature
    """
    return sign_and_verify(private_key, message, address)


def is_compressed(priv_key):
    if priv_key[0] in ['L', 'K', 'c']:  # mainnet: L or K, testnet: c
        compressed = True
    elif priv_key[0] in ['5', '9']:  # mainnet: 5, testnet: 9
        compressed = False
    else:
        raise BaseException("error: private key must start with 5 (mainnet) or 9 (testnet) if uncompressed or L/K (mainnet) or c (testnet) for compressed")

    return compressed

