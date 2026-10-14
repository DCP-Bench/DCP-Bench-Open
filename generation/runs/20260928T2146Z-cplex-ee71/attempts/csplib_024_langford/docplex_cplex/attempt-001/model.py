"""Langford's problem: arrange two copies of 1..k in a row so that the two copies of i have exactly i numbers between them."""
from docplex.mp.model import Model


def build(instance):
    k = instance["k"]
    length = 2 * k
    numbers = range(1, k + 1)

    model = Model("langford")

    # starts[i, p] is 1 when the first copy of i is at position p; the second
    # copy is then at p + i + 1, which must still be in the row.
    starts = {(i, p): model.binary_var(name=f"starts_{i}_{p}") for i in numbers for p in range(length - i - 1)}

    # Each number is placed exactly once (its pair of copies).
    for i in numbers:
        model.add_constraint(model.sum(v for (j, p), v in starts.items() if j == i) == 1, ctname=f"place_{i}")

    # covers[q] lists the placements that put a copy at position q.
    covers = {q: [] for q in range(length)}
    for (i, p) in starts:
        covers[p].append((i, p))
        covers[p + i + 1].append((i, p))

    # Every position of the row holds exactly one copy.
    for q in range(length):
        model.add_constraint(model.sum(starts[key] for key in covers[q]) == 1, ctname=f"position_{q}")

    # The number at each position, read back from the placements.
    sol = [model.sum(i * starts[i, p] for (i, p) in covers[q]) for q in range(length)]
    return model, {"sol": sol}
