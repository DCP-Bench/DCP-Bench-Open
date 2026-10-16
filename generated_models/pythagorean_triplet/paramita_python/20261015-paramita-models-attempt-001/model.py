# Pythagorean triplet: a, b, c natural numbers with a < b < c, a^2 + b^2 = c^2, a + b + c = 1000.
# Each integer is a unary (order) form: u[i] is true when the value is greater than i.
# Bounds from a < b < c and a + b + c = 1000: a <= 332, b <= 499, c <= 998.
from paramita.modelling import Bool, If

SQUARE_BITS = 20  # 998^2 < 2^20


def total(xs):
    """Sum of Bools as a balanced tree, so the expression stays shallow."""
    xs = list(xs)
    while len(xs) > 1:
        xs = [xs[i] + xs[i + 1] if i + 1 < len(xs) else xs[i] for i in range(0, len(xs), 2)]
    return xs[0]


def unary(name, length):
    """u[i] is true when the value is greater than i; u[i+1] implies u[i]."""
    u = [Bool(f"{name}_gt_{i}") for i in range(length)]
    cons = [If(u[i + 1], u[i]) for i in range(length - 1)]
    return u, cons


def binary_square(u, name):
    """Binary bits of the square of the unary value u: for each value v, the exact
    value v makes the bits equal the binary digits of v*v."""
    s = [Bool(f"{name}_sq_bit_{k}") for k in range(SQUARE_BITS)]
    cons = []
    for v in range(1, len(u) + 1):
        exactly_v = u[v - 1] & ~u[v] if v < len(u) else u[v - 1]
        for k in range(SQUARE_BITS):
            bit = ((v * v) >> k) & 1
            cons.append(If(exactly_v, s[k] if bit else ~s[k]))
    value = sum((1 << k) * s[k] for k in range(SQUARE_BITS))
    return value, cons


def build(instance):
    # the upper bounds are fixed by the problem statement (see the header comment)
    a, cons_a = unary("a", 332)
    b, cons_b = unary("b", 499)
    c, cons_c = unary("c", 998)
    cons = cons_a + cons_b + cons_c

    # natural numbers start at 1
    cons += [a[0], b[0], c[0]]

    # a < b < c
    cons.append(total(a) + 1 <= total(b))
    cons.append(total(b) + 1 <= total(c))

    # a + b + c = 1000
    cons.append(total(a) + total(b) + total(c) == 1000)

    # a^2 + b^2 = c^2, with the squares held in binary
    a_sq, cons_a_sq = binary_square(a, "a")
    b_sq, cons_b_sq = binary_square(b, "b")
    c_sq, cons_c_sq = binary_square(c, "c")
    cons += cons_a_sq + cons_b_sq + cons_c_sq
    cons.append(a_sq + b_sq == c_sq)

    outputs = {"a": total(a), "b": total(b), "c": total(c)}
    return cons, outputs
