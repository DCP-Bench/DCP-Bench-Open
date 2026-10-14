# Curious numbers (Dudeney): 48 is a number such that adding 1 to it gives a square
# and adding 1 to its half also gives a square. Find another such number between
# 1 and 10000.
import z3


def build(instance):
    del instance  # the puzzle states its own range and known number

    limit = 10000  # numbers considered lie between 1 and 10000
    known = 48     # the known number with this peculiarity

    # peculiar: the number. plus_one = peculiar + 1 and root_a its square root.
    # half = peculiar / 2, half_plus_one = half + 1 and root_b its square root.
    peculiar, plus_one, root_a, half, half_plus_one, root_b = z3.Ints(
        "peculiar plus_one root_a half half_plus_one root_b")

    solver = z3.Solver()
    for v in (peculiar, plus_one, root_a, half, half_plus_one, root_b):
        solver.add(v >= 1, v <= limit)

    # We want a number other than the known one.
    solver.add(peculiar != known)

    # Adding 1 to the number gives a square number.
    solver.add(plus_one == peculiar + 1)
    solver.add(plus_one == root_a * root_a)

    # Adding 1 to half the number also gives a square number.
    solver.add(peculiar == 2 * half)
    solver.add(half_plus_one == half + 1)
    solver.add(half_plus_one == root_b * root_b)

    return solver, {"peculiar": peculiar}
