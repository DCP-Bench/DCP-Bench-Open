# KenKen: fill an n x n grid with 1..n so that each row and column holds every
# digit once, and each cage of cells achieves its target. A cage of two cells
# reaches it by a sum, product, difference or quotient; a larger cage by its sum
# or its product. Digits may repeat inside a cage.
from ortools.sat.python import cp_model


def build(instance):
    n = instance["n"]
    cages = instance["problem"]  # [target, [[row, column], ...]] with cells counted from 1

    model = cp_model.CpModel()

    # x[r][c] = the digit in cell (r, c)
    x = [[model.new_int_var(1, n, f"x_{r}_{c}") for c in range(n)] for r in range(n)]

    # each row and each column holds different digits
    for r in range(n):
        model.add_all_different(x[r])
    for c in range(n):
        model.add_all_different([x[r][c] for r in range(n)])

    def holds(condition):
        """A Boolean that is true only when the condition holds."""
        literal = model.new_bool_var("way")
        model.add(condition).only_enforce_if(literal)
        return literal

    for target, cells in cages:
        cage = [x[r - 1][c - 1] for r, c in cells]
        # the product of the digits of the cage (CP-SAT multiplies variables in a separate constraint)
        product = model.new_int_var(1, n ** len(cage), "cage_product")
        model.add_multiplication_equality(product, cage)

        if len(cage) == 2:
            a, b = cage
            ways = [
                holds(a + b == target),  # sum
                holds(product == target),  # product
                holds(a * target == b),  # quotient: b divided by a is the target
                holds(b * target == a),  # quotient the other way round
                holds(a - b == target),  # difference
                holds(b - a == target),  # difference the other way round
            ]
        else:
            # a larger cage adds up to the target or multiplies to it
            ways = [holds(sum(cage) == target), holds(product == target)]
        # the cage reaches its target in at least one of these ways
        model.add_bool_or(ways)

    return model, {"x": x}
