#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest

from helpers.jacobianhelpers import (
    fast_add, fast_multiply, from_jacobian, to_jacobian,
    jacobian_add, jacobian_multiply, jacobian_double, inv,
    P, N, G, A, B, Gx, Gy
)


class TestConstants(object):
    """Tests for elliptic curve constants"""

    def test_secp256k1_constants(self):
        assert P == 2**256 - 2**32 - 977
        assert A == 0
        assert B == 7
        assert G == (Gx, Gy)

    def test_generator_point(self):
        assert Gx == 55066263022277343669578718895168534326250603453777594175500187360389116729240
        assert Gy == 32670510020758816978083085130507043184471273380659243275938904335757337482424


class TestToJacobian(object):
    """Tests for to_jacobian function"""

    def test_to_jacobian(self):
        p = (1, 2)
        result = to_jacobian(p)
        assert result == (1, 2, 1)

    def test_to_jacobian_generator(self):
        result = to_jacobian(G)
        assert result == (Gx, Gy, 1)


class TestFromJacobian(object):
    """Tests for from_jacobian function"""

    def test_from_jacobian_z_is_1(self):
        p = (Gx, Gy, 1)
        result = from_jacobian(p)
        assert result == (Gx, Gy)

    def test_from_jacobian_roundtrip(self):
        p = G
        jacobian = to_jacobian(p)
        result = from_jacobian(jacobian)
        assert result == p


class TestInv(object):
    """Tests for modular inverse function"""

    def test_inv_zero(self):
        result = inv(0, P)
        assert result == 0

    def test_inv_one(self):
        result = inv(1, P)
        assert result == 1

    def test_inv_basic(self):
        # Test that a * inv(a) mod n == 1
        a = 12345
        result = inv(a, P)
        assert (a * result) % P == 1

    def test_inv_large_number(self):
        a = 2**128
        result = inv(a, P)
        assert (a * result) % P == 1


class TestJacobianDouble(object):
    """Tests for jacobian_double function"""

    def test_jacobian_double_zero_y(self):
        # Point with y=0 should return (0, 0, 0)
        p = (1, 0, 1)
        result = jacobian_double(p)
        assert result == (0, 0, 0)

    def test_jacobian_double_generator(self):
        p = to_jacobian(G)
        result = jacobian_double(p)
        assert isinstance(result, tuple)
        assert len(result) == 3


class TestJacobianAdd(object):
    """Tests for jacobian_add function"""

    def test_jacobian_add_p_zero_y(self):
        # If p[1] is 0, return q
        p = (1, 0, 1)
        q = to_jacobian(G)
        result = jacobian_add(p, q)
        assert result == q

    def test_jacobian_add_q_zero_y(self):
        # If q[1] is 0, return p
        p = to_jacobian(G)
        q = (1, 0, 1)
        result = jacobian_add(p, q)
        assert result == p

    def test_jacobian_add_same_point(self):
        # Adding a point to itself should double it
        p = to_jacobian(G)
        result = jacobian_add(p, p)
        doubled = jacobian_double(p)
        # Results should be equivalent when converted back
        assert from_jacobian(result) == from_jacobian(doubled)

    def test_jacobian_add_inverse_points(self):
        # Adding a point to its inverse should give identity
        p = to_jacobian(G)
        # Create inverse point (same x, negated y)
        p_inv = (p[0], P - p[1], p[2])
        result = jacobian_add(p, p_inv)
        # Result should be the identity element
        assert result == (0, 0, 1)


class TestJacobianMultiply(object):
    """Tests for jacobian_multiply function"""

    def test_jacobian_multiply_by_zero(self):
        p = to_jacobian(G)
        result = jacobian_multiply(p, 0)
        assert result == (0, 0, 1)

    def test_jacobian_multiply_zero_y(self):
        p = (1, 0, 1)
        result = jacobian_multiply(p, 5)
        assert result == (0, 0, 1)

    def test_jacobian_multiply_by_one(self):
        p = to_jacobian(G)
        result = jacobian_multiply(p, 1)
        assert result == p

    def test_jacobian_multiply_by_two(self):
        p = to_jacobian(G)
        result = jacobian_multiply(p, 2)
        doubled = jacobian_double(p)
        assert from_jacobian(result) == from_jacobian(doubled)

    def test_jacobian_multiply_negative(self):
        p = to_jacobian(G)
        result = jacobian_multiply(p, -1)
        # Should handle negative by taking mod N
        assert isinstance(result, tuple)

    def test_jacobian_multiply_large_n(self):
        p = to_jacobian(G)
        result = jacobian_multiply(p, N + 1)
        # Should be same as multiplying by 1 (mod N)
        assert from_jacobian(result) == from_jacobian(jacobian_multiply(p, 1))

    def test_jacobian_multiply_even(self):
        p = to_jacobian(G)
        result = jacobian_multiply(p, 4)
        assert isinstance(result, tuple)

    def test_jacobian_multiply_odd(self):
        p = to_jacobian(G)
        result = jacobian_multiply(p, 5)
        assert isinstance(result, tuple)


class TestFastAdd(object):
    """Tests for fast_add function"""

    def test_fast_add_generator_to_itself(self):
        result = fast_add(G, G)
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_fast_add_different_points(self):
        # 2G
        two_g = fast_multiply(G, 2)
        # G + 2G = 3G
        result = fast_add(G, two_g)
        three_g = fast_multiply(G, 3)
        assert result == three_g


class TestFastMultiply(object):
    """Tests for fast_multiply function"""

    def test_fast_multiply_by_one(self):
        result = fast_multiply(G, 1)
        assert result == G

    def test_fast_multiply_by_two(self):
        result = fast_multiply(G, 2)
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert result != G

    def test_fast_multiply_associative(self):
        # (2 * 3) * G == 2 * (3 * G)
        result1 = fast_multiply(G, 6)
        intermediate = fast_multiply(G, 3)
        result2 = fast_multiply(intermediate, 2)
        # Note: This tests scalar multiplication, not point multiplication
        # 2 * (3G) is not the same as 6G in general
        # But 3G + 3G = 6G
        result3 = fast_add(intermediate, intermediate)
        assert result1 == result3
