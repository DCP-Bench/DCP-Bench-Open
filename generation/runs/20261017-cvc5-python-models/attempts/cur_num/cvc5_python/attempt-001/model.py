# Problem cur_num: print another number with the peculiarity (peculiar) between
# 1 and 10000. The number 48 has the peculiarity: adding 1 to it gives a square,
# and adding 1 to its half also gives a square. "Another" excludes 48.
import math

import cvc5.pythonic as cz

LOWER = 1
UPPER = 10000
EXAMPLE = 48


def build(instance):
    peculiar = cz.Int("peculiar")

    # Bounds from the description: a number between 1 and 10000.
    constraints = [peculiar >= LOWER, peculiar <= UPPER]

    # Another number than the example 48.
    constraints.append(peculiar != EXAMPLE)

    # Adding 1 to the number gives a square number. The square root of the
    # largest value that can be reached, UPPER + 1, bounds the root.
    # The root is a Python constant per disjunct, so every constraint is linear.
    root_limit = math.isqrt(UPPER + 1)
    constraints.append(
        cz.Or([peculiar + 1 == k * k for k in range(1, root_limit + 1)])
    )

    # Adding 1 to its half also gives a square number. The half is an integer,
    # so the number is even: peculiar == 2 * (m * m - 1) for some m >= 1.
    half_root_limit = math.isqrt((UPPER + 2) // 2) + 1
    constraints.append(
        cz.Or([peculiar == 2 * (m * m - 1) for m in range(1, half_root_limit + 1)])
    )

    return constraints, {"peculiar": peculiar}
