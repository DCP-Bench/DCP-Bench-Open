# Fewest raw rolls cut, using the given patterns to meet every order.
#
# The instance also carries roll_width and the widths themselves. The reference
# uses neither in a constraint, only len(widths): the patterns in
# num_rolls_width already encode what fits on a roll.
from exact import Exact


def build(instance):
    orders = instance["orders"]
    num_patterns = instance["num_patterns"]
    per_pattern = instance["num_rolls_width"]
    widths = len(instance["widths"])

    # 0..100 uses of each pattern is the bound the reference declares.
    solver = Exact()
    used = [f"u{j}" for j in range(num_patterns)]
    for name in used:
        solver.addVariable(name, 0, 100)
    for i in range(widths):
        solver.addConstraint(
            [(per_pattern[j][i], used[j]) for j in range(num_patterns)
             if per_pattern[j][i]], True, orders[i])

    solver.addVariable("rolls", 0, 100 * num_patterns)
    solver.addConstraint([(1, name) for name in used] + [(-1, "rolls")],
                         True, 0, True, 0)
    return (solver, {"patterns_used": used, "min_rolls_cut": "rolls"},
            ("minimize", [(1, "rolls")]))
