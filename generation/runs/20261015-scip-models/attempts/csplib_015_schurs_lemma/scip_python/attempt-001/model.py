# Schur's lemma: put balls 1..n into 3 boxes so that no triple (x, y, z) with x + y = z
# has all three balls in the same box.
from pyscipopt import Model, quicksum


def build(instance):
    n = instance["n"]
    boxes = 3
    m = Model()

    # M[i, j] = 1 if ball i+1 is in box j+1 (0-based indices in the code)
    M = {(i, j): m.addVar(name=f"M_{i}_{j}", vtype="B") for i in range(n) for j in range(boxes)}

    # a ball must be in exactly one box
    for i in range(n):
        m.addCons(quicksum(M[i, j] for j in range(boxes)) == 1, name=f"one_box_{i}")

    # for each x + y = z with 1 <= x <= y and z <= n, and each box j,
    # not all of x, y, z are in box j: M[x,j] + M[y,j] + M[z,j] <= 2
    # (x = y is allowed, as in the description; then the term M[x,j] appears twice)
    for x in range(1, n + 1):
        for y in range(x, n + 1):
            z = x + y
            if z > n:
                break
            for j in range(boxes):
                m.addCons(
                    quicksum(M[k - 1, j] for k in (x, y, z)) <= 2,
                    name=f"no_mono_{x}_{y}_{z}_{j}",
                )

    # the output gives the box of each ball, numbered from 1 to 3
    balls = [quicksum((j + 1) * M[i, j] for j in range(boxes)) for i in range(n)]
    return m, {"balls": balls}
