# Curious set of integers (Martin Gardner): 1, 3, 8 and 120 form a set in which the
# product of any two integers is one less than a perfect square. Find a further
# number, at least 0, that can be added to the set without destroying this property.
import z3


def build(instance):
    n = instance["n"]              # size of the set once the new number is added
    max_val = instance["max_val"]  # largest value any element or square root may take

    # Problem data (fixed by the puzzle text): the first four members of the set.
    given = [1, 3, 8, 120]

    # x[i] = the ith member of the set; the last one is the number to find.
    x = z3.IntVector("x", n)
    number = x[n - 1]

    solver = z3.Solver()
    for v in x:
        solver.add(v >= 0, v <= max_val)

    # The members of the set are different.
    solver.add(z3.Distinct(x))

    # The first four members are the given ones.
    for i in range(min(n, len(given))):
        solver.add(x[i] == given[i])

    # The product of any two members is one less than a perfect square: there is
    # an integer root with root * root == product + 1. The condition is symmetric
    # in the pair, so each pair is posted once.
    for i in range(n):
        for j in range(i + 1, n):
            root = z3.Int(f"root_{i}_{j}")
            solver.add(root >= 0, root <= max_val)
            solver.add(root * root == x[i] * x[j] + 1)

    return solver, {"number": number}
