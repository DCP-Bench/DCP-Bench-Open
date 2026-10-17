# csplib 022 bus driver scheduling: choose shifts so that every piece of work is covered exactly once,
# minimising the number of selected shifts. Output x[j] is true when shift j is selected.
import cvc5.pythonic as cz


def build(instance):
    num_work = instance["num_work"]
    num_shifts = instance["num_shifts"]
    shifts = instance["shifts"]

    x = [cz.Bool(f"x_{j}") for j in range(num_shifts)]

    # Each piece of work is covered by exactly one selected shift.
    constraints = []
    for w in range(num_work):
        covering = [j for j in range(num_shifts) if w in shifts[j]]
        if not covering:
            constraints.append(cz.BoolVal(False))
        else:
            constraints.append(cz.Sum([cz.If(x[j], 1, 0) for j in covering]) == 1)

    # The cost of each shift is equal: minimise the number of selected shifts.
    cost = cz.Sum([cz.If(x[j], 1, 0) for j in range(num_shifts)])

    return constraints, {"x": x}, ("minimize", cost)
