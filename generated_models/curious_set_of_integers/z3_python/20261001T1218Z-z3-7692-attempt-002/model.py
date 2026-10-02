# Curious set of integers (Martin Gardner): 1, 3, 8 and 120 form a set in which the
# product of any two integers is one less than a perfect square. Find a further
# number, at least 0, that can be added to the set without destroying this property.
import z3


def build(instance):
    n = instance["n"]              # size of the set once the new number is added
    max_val = instance["max_val"]  # largest value any element or square root may take

    # Problem data (fixed by the puzzle text): the first four members of the set.
    given = [1, 3, 8, 120]

    # Bit-vector encoding: products and squares of integers up to max_val are
    # bit-blasted to SAT, which settles that no further number exists far faster
    # than Z3's nonlinear integer arithmetic does.
    bits = max_val.bit_length()   # bits for a value between 0 and max_val
    wide = 2 * bits + 1           # bits for a product of two values, plus one

    def widen(bv):
        return z3.ZeroExt(wide - bits, bv)

    # x[i] = the ith member of the set; the last one is the number to find.
    x = [z3.BitVec(f"x_{i}", bits) for i in range(n)]
    number = x[n - 1]

    solver = z3.Solver()
    for v in x:
        solver.add(z3.ULE(v, max_val))

    # The members of the set are different.
    solver.add(z3.Distinct(x))

    # The first four members are the given ones.
    for i in range(min(n, len(given))):
        solver.add(x[i] == given[i])

    # The product of any two members is one less than a perfect square: there is
    # a root, at most max_val, with root * root == product + 1. The condition is
    # symmetric in the pair, so each pair is posted once.
    for i in range(n):
        for j in range(i + 1, n):
            root = z3.BitVec(f"root_{i}_{j}", bits)
            solver.add(z3.ULE(root, max_val))
            solver.add(widen(root) * widen(root) == widen(x[i]) * widen(x[j]) + 1)

    return solver, {"number": z3.BV2Int(number)}
