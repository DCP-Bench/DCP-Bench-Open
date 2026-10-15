# Find another peculiar number between 1 and 10000: a number p such that
# p + 1 is a square and p/2 + 1 is a square. The number 48 is excluded.
from math import isqrt

from paramita.modelling import Bool, Or

LIMIT = 10000  # the problem's upper bound on the number
BITS = LIMIT.bit_length()  # 14 bits for values up to 10000


def build(instance):
    # The problem has no instance fields; the bounds above come from the statement.

    # peculiar number as binary digits: peculiar = sum 2^k * bit_k
    bits = [Bool(f"peculiar_bit_{k}") for k in range(BITS)]
    peculiar = sum((2**k) * bits[k] for k in range(BITS))
    cons = []

    # the number lies between 1 and 10000
    cons.append(peculiar >= 1)
    cons.append(peculiar <= LIMIT)

    # the number is different from 48
    cons.append(Or(peculiar <= 47, peculiar >= 49))

    # if you add 1 to the number the result is a square number:
    # exactly one root a in 1..100 (a*a <= 10001) with a*a == peculiar + 1
    max_root = isqrt(LIMIT + 1)
    root_a = {a: Bool(f"root_a_{a}") for a in range(1, max_root + 1)}
    cons.append(sum(root_a.values()) == 1)
    cons.append(sum(a * a * root_a[a] for a in root_a) == peculiar + 1)

    # its half is even: the number's lowest bit is 0, so half = peculiar / 2
    cons.append(~bits[0])
    half = sum((2**k) * bits[k + 1] for k in range(BITS - 1))

    # if you add 1 to its half you also get a square number:
    # exactly one root b with b*b == half + 1 (half <= 5000, so b <= 70)
    max_half_root = isqrt(LIMIT // 2 + 1)
    root_b = {b: Bool(f"half_root_{b}") for b in range(1, max_half_root + 1)}
    cons.append(sum(root_b.values()) == 1)
    cons.append(sum(b * b * root_b[b] for b in root_b) == half + 1)

    return cons, {"peculiar": peculiar}
