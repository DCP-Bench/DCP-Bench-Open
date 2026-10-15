# Find a number x >= 0 that can be added to the set {1, 3, 8, 120}: for every
# pair of integers in the set, their product is one less than a perfect square.
# The pairs formed with the new number x are a*x + 1 for each a in the set.
from math import isqrt

from paramita.modelling import Bool

KNOWN = [1, 3, 8, 120]  # the given set from the problem statement


def build(instance):
    max_val = instance["max_val"]  # the upper bound on the new number
    n = instance["n"]  # size of the set once the new number is added
    assert len(KNOWN) + 1 == n
    bits_count = max_val.bit_length()

    # the new number as binary digits: x = sum 2^k * bit_k
    bits = [Bool(f"x_bit_{k}") for k in range(bits_count)]
    number = sum((2**k) * bits[k] for k in range(bits_count))
    cons = []

    # the number is at most max_val
    cons.append(number <= max_val)

    # the product of each set element a with the new number is one less than a square:
    # a*x + 1 == c*c for some c, with c one-hot over the possible roots
    for a in KNOWN:
        max_root = isqrt(a * max_val + 1)
        roots = {c: Bool(f"root_{a}_{c}") for c in range(1, max_root + 1)}
        cons.append(sum(roots.values()) == 1)
        cons.append(sum(c * c * roots[c] for c in roots) == a * number + 1)

    return cons, {"number": number}
