# Four numbers: given up to four distinct integers between 1 and 10, find three
# integers between 1 and 10 such that every given number is the sum of some
# subset of the three.
from exact import Exact


def build(instance):
    numbers = instance["numbers"]
    n = 3  # how many integers are to be found

    solver = Exact()
    # x[j] = the j-th of the three integers
    x = [f"x_{j}" for j in range(n)]
    for name in x:
        solver.addVariable(name, 1, 10)

    for i, target in enumerate(numbers):
        parts = []
        for j in range(n):
            # use_i_j = 1 when x[j] belongs to the subset that makes numbers[i]
            use = f"use_{i}_{j}"
            # part_i_j = use_i_j * x[j]: the value x[j] contributes to numbers[i]
            part = f"part_{i}_{j}"
            solver.addVariable(use, 0, 1)
            solver.addVariable(part, 0, 10)
            solver.addMultiplication([use, x[j]], True, part, True, part)
            parts.append((1, part))
        # the chosen subset adds up to the given number
        solver.addConstraint(parts, True, target, True, target)

    return solver, {"x": x}
