# Bowls and oranges: place m oranges in n bowls in a line (1 metre apart), at most one
# orange per bowl, so that no three oranges A, B, C have dist(A, B) = dist(B, C).
# Output x: the bowl numbers (1 to n, ascending) holding the oranges.
from pyscipopt import Model, quicksum


def build(instance):
    n = instance["n"]
    m = instance["m"]
    model = Model()

    # y[i, k] = 1 if orange k is in bowl i + 1
    y = {(i, k): model.addVar(name=f"y_{i}_{k}", vtype="B") for i in range(n) for k in range(m)}

    # every orange is in exactly one bowl
    for k in range(m):
        model.addCons(quicksum(y[i, k] for i in range(n)) == 1)

    # no more than one orange in each bowl
    occupied = [quicksum(y[i, k] for k in range(m)) for i in range(n)]
    for i in range(n):
        model.addCons(occupied[i] <= 1)

    # no three oranges in arithmetic progression: bowls i, i + d, i + 2d
    # cannot all hold an orange
    for i in range(n):
        for d in range(1, n):
            if i + 2 * d >= n:
                break
            model.addCons(occupied[i] + occupied[i + d] + occupied[i + 2 * d] <= 2)

    # the oranges are numbered by bowl in ascending order (this breaks the symmetry
    # between orange labels)
    pos = [quicksum((i + 1) * y[i, k] for i in range(n)) for k in range(m)]
    for k in range(m - 1):
        model.addCons(pos[k] + 1 <= pos[k + 1])

    return model, {"x": pos}
