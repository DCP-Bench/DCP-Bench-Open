# KenKen: fill an n x n grid with 1..n so that each row and column holds every
# digit once, and each cage of cells achieves its target. A cage of two cells
# reaches it by a sum, product, difference or quotient; a larger cage by its sum
# or its product. Digits may repeat inside a cage.
from pychoco.model import Model


def build(instance):
    n = instance["n"]
    cages = instance["problem"]  # [target, [[row, column], ...]] with cells counted from 1

    model = Model()

    # x[r][c] = the digit in cell (r, c)
    x = [[model.intvar(1, n, name=f"x_{r}_{c}") for c in range(n)] for r in range(n)]

    # each row and each column holds different digits
    for r in range(n):
        model.all_different(x[r]).post()
    for c in range(n):
        model.all_different([x[r][c] for r in range(n)]).post()

    for k, (target, cells) in enumerate(cages):
        cage = [x[r - 1][c - 1] for r, c in cells]
        if len(cage) == 2:
            a, b = cage
            # the cage reaches its target in at least one of these ways
            model.or_([
                model.arithm(a, "+", b, "=", target),  # sum
                model.times(a, b, target),  # product
                model.times(a, target, b),  # quotient: b divided by a is the target
                model.times(b, target, a),  # quotient the other way round
                model.arithm(a, "-", b, "=", target),  # difference
                model.arithm(b, "-", a, "=", target),  # difference the other way round
            ]).post()
        else:
            # the product of the digits, built one multiplication at a time
            product = cage[0]
            for step, cell in enumerate(cage[1:]):
                bigger = model.intvar(1, n ** (step + 2), name=f"cage_{k}_product_{step}")
                model.times(product, cell, bigger).post()
                product = bigger
            # a larger cage adds up to the target or multiplies to it
            model.or_([model.sum(cage, "=", target), model.arithm(product, "=", target)]).post()

    return model, {"x": x}
