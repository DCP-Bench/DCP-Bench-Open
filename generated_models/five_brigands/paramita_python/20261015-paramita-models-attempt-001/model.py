"""Five Spanish brigands and their doubloons.

Alfonso (A), Benito (B), Carlos (C), Diego (D) and Esteban (E) captured exactly
200 doubloons altogether. Had Alfonso twelve times as much, Benito three times,
Carlos the same, Diego half and Esteban one third, the total would still be 200.
Each brigand has at least one doubloon. Output: the doubloons of A, B, C, D, E.

Encoding: each count is an integer in 1..200, written in unary (order Bools
x_ge_k meaning "count >= k", for k = 2..200, chained so x_ge_k implies
x_ge_{k-1}). The 200 bound is the total from the description.
"""

from paramita.modelling import Bool, If

TOTAL = 200
NAMES = ["A", "B", "C", "D", "E"]


def unary_count(name):
    """Unary integer in 1..TOTAL: value = 1 + sum of order Bools."""
    ge = {k: Bool(f"{name}_ge_{k}") for k in range(2, TOTAL + 1)}
    cons = [If(ge[k], ge[k - 1]) for k in range(3, TOTAL + 1)]
    value = 1 + sum(ge.values())
    return value, cons


def build(instance):
    cons = []
    value = {}
    for name in NAMES:
        value[name], c = unary_count(name)
        cons += c
    A, B, C, D, E = (value[n] for n in NAMES)

    # the five captured together exactly 200 doubloons
    cons.append(A + B + C + D + E == TOTAL)

    # with Alfonso x12, Benito x3, Carlos x1, Diego x1/2, Esteban x1/3 the total is still 200;
    # multiplied by 6 so every coefficient is an integer: 72A + 18B + 6C + 3D + 2E = 1200
    cons.append(72 * A + 18 * B + 6 * C + 3 * D + 2 * E == 6 * TOTAL)

    # no brigand had less than one doubloon: unary_count starts at 1, so every
    # count is at least 1 by construction (no extra constraint)

    return cons, {"A": A, "B": B, "C": C, "D": D, "E": E}
