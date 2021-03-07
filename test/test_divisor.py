import pytest
from functools import reduce
from hypothesis import given
from hypothesis import settings
from numba.typed import List

from riemann.divisor import divisor_sum
from riemann.divisor import prime_factor_divisor_sum

from riemann.primes import primes

import hypothesis.strategies as st


divisor_sums = [
    1, 3, 4, 7, 6, 12, 8, 15, 13, 18, 12, 28, 14, 24, 24, 31, 18, 39, 20, 42, 32,
    36, 24, 60, 31, 42, 40, 56, 30, 72, 32, 63, 48, 54, 48, 91, 38, 60, 56, 90, 42,
    96, 44, 84, 78, 72, 48, 124, 57, 93, 72
]

input_output_pairs = zip(range(1, len(divisor_sums) + 1), divisor_sums)

@pytest.mark.parametrize("test_input,expected", input_output_pairs)
def test_sum_of_divisors(test_input, expected):
    assert divisor_sum(test_input) == expected


def test_sum_of_divisors_of_1():
    assert 1 == divisor_sum(1)


def test_sum_of_divisors_of_72():
    assert 195 == divisor_sum(72)

@st.composite
def prime_factorization(draw):
    '''Draw a random prime factorization.
    This function is a bit finnicky because when the number whose
    prime factorization is chosen here is too large, then the
    test either slows to a crawl (because it's computing a naive
    divisor sum as the ground truth), or it hits an integer max
    value and overflows.
    '''
    indexes = draw(
        st.lists(st.integers(min_value=0, max_value=10),
                 min_size=1,
                 max_size=4,
                 unique=True))
    bases = [primes[i] for i in indexes]
    powers = draw(
        st.lists(st.integers(min_value=1, max_value=3),
                 min_size=len(bases),
                 max_size=len(bases)))
    return list(zip(bases, powers))


@settings(deadline=1000)
@given(prime_factorization())
def test_prime_factor_divisor_sum(prime_factorization):
    n = reduce(lambda x, y: x * y, (p**a for (p, a) in prime_factorization))
    print(n)
    assert prime_factor_divisor_sum(List(prime_factorization)) == divisor_sum(n)


def test_prime_factor_divisor_sum_2():
    assert prime_factor_divisor_sum(List([(2, 1)])) == divisor_sum(2)

