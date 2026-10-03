"""Project Euler 9: the Pythagorean triplet a^2 + b^2 = c^2 with a + b + c = 1000."""
from docplex.mp.model import Model


def build(instance):
    # The problem has no instance data. The sum 1000 is from the statement; each number is
    # in 1..500, the domain the reference declares.
    total = 1000
    top = 500

    model = Model("pythagorean_triplet")
    model.parameters.mip.tolerances.integrality = 0

    a = model.integer_var(1, top, name="a")
    b = model.integer_var(1, top, name="b")
    c = model.integer_var(1, top, name="c")

    # The three numbers add up to 1000.
    model.add_constraint(a + b + c == total)

    # a^2 + b^2 = c^2. CPLEX refuses this non-convex quadratic equality. With
    # c = 1000 - a - b it is the same as a^2 + b^2 = (1000 - a - b)^2, which simplifies to
    # a * b = 1000 * a + 1000 * b - 500000, so only the product a * b is needed. It is
    # written through the binary digits of a: a = sum 2^i bit_i and
    # a * b = sum 2^i (bit_i * b), each bit_i * b a binary times an integer in 0..500.
    width = top.bit_length()
    bit = [model.binary_var(name=f"a_bit_{i}") for i in range(width)]
    model.add_constraint(a == model.sum(2 ** i * bit[i] for i in range(width)))
    partial = []
    for i in range(width):
        p = model.integer_var(0, top, name=f"b_times_bit_{i}")
        model.add_constraint(p <= top * bit[i])
        model.add_constraint(p <= b)
        model.add_constraint(p >= b - top * (1 - bit[i]))
        partial.append(2 ** i * p)
    model.add_constraint(2 * model.sum(partial) == 2 * total * a + 2 * total * b - total * total)

    return model, {"a": a, "b": b, "c": c}
