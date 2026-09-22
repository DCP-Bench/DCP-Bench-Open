# Make the exact amount from the available coins, using as few coins as possible.
from exact import Exact


def build(instance):
    amount = instance["amount"]
    types = instance["types_of_coins"]
    available = instance["available_coins"]
    n = len(types)

    solver = Exact()
    counts = [f"c{i}" for i in range(n)]
    for i, name in enumerate(counts):
        solver.addVariable(name, 0, available[i])
    solver.addConstraint(list(zip(types, counts)), True, amount, True, amount)
    return (solver, {"coin_counts": counts},
            ("minimize", [(1, name) for name in counts]))
