"""Five brigands (Dudeney 133): five brigands hold 200 doubloons in all; with twelve times,
three times, the same, half and a third of their shares they would still hold 200. How many
doubloons has each?
"""
from docplex.mp.model import Model


def build(instance):
    # The problem has no instance data; the total 200 and the multipliers are from the
    # statement. No brigand has less than one doubloon.
    total = 200
    model = Model("five_brigands")
    names = ["A", "B", "C", "D", "E"]
    share = {x: model.integer_var(1, total, name=x) for x in names}
    A, B, C, D, E = (share[x] for x in names)

    # Altogether they captured exactly 200 doubloons.
    model.add_constraint(A + B + C + D + E == total)
    # 12 A + 3 B + C + D / 2 + E / 3 is also 200; multiplied by 6 to keep integers.
    model.add_constraint(6 * (12 * A + 3 * B + C) + 3 * D + 2 * E == 6 * total)

    return model, dict(share)
