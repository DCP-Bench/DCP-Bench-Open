# Fewest items from whole packs that still meet the target.
from exact import Exact


def build(instance):
    packs = instance["packs"]
    target = instance["target"]
    n = len(packs)

    # The reference allows up to twice the target of each pack size.
    ceiling = target * 2
    solver = Exact()
    counts = [f"c{i}" for i in range(n)]
    for name in counts:
        solver.addVariable(name, 0, ceiling)

    solver.addVariable("total", 0, ceiling * n)
    solver.addConstraint(list(zip(packs, counts)) + [(-1, "total")],
                         True, 0, True, 0)
    solver.addConstraint([(1, "total")], True, target)
    return solver, {"counts": counts}, ("minimize", [(1, "total")])
