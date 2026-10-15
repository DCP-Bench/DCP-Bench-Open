# Bowls and oranges: place m oranges in n bowls on a line (bowls 1..n, 1 metre apart),
# at most one orange per bowl, and no three oranges A, B, C with dist(A, B) == dist(B, C),
# i.e. no three bowls in arithmetic progression.
# Output x: the bowls holding the oranges, in ascending order.
from paramita.modelling import Bool, Iff, Or


def build(instance):
    n, m = instance["n"], instance["m"]
    bowls = range(1, n + 1)

    # pos[k][i]: the k-th orange (in ascending order) lies in bowl i
    pos = [{i: Bool(f"orange_{k}_in_bowl_{i}") for i in bowls} for k in range(m)]
    # occ[i]: bowl i holds an orange
    occ = {i: Bool(f"bowl_{i}_has_orange") for i in bowls}

    cons = []

    # each orange lies in exactly one bowl
    cons += [sum(pos[k].values()) == 1 for k in range(m)]

    # a bowl holds an orange exactly when some orange is placed in it
    # (one orange per bowl follows from the strict ordering of the oranges below)
    cons += [Iff(occ[i], Or([pos[k][i] for k in range(m)])) for i in bowls]

    # oranges sit in distinct bowls, in ascending order
    positions = [sum(i * pos[k][i] for i in bowls) for k in range(m)]
    cons += [positions[k] + 1 <= positions[k + 1] for k in range(m - 1)]

    # no three oranges in arithmetic progression: bowls i, i+d, i+2d are never all occupied
    for i in bowls:
        for d in range(1, n):
            if i + 2 * d > n:
                break
            cons.append(~(occ[i] & occ[i + d] & occ[i + 2 * d]))

    return cons, {"x": positions}
