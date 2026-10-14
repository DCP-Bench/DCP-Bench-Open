"""Broken weights: a measuring weight of m pounds broke into n pieces, each of a
whole number of pounds. Find the weights of the pieces so that, on a balance
scale, they can weigh every whole weight from 1 to m pounds.

A piece may go on the same pan as the object, on the other pan, or stay off the
scale. The weights are not required to be listed in any particular order.
"""
import pulp


def build(instance):
    m = instance["m"]  # total weight of the original weight, all pieces together
    n = instance["n"]  # number of pieces

    problem = pulp.LpProblem("broken_weights", pulp.LpMinimize)

    # A piece weighs at least 1 and the other n - 1 pieces weigh at least 1 each,
    # so a piece weighs between 1 and m - (n - 1) pounds.
    top = m - (n - 1)
    values = range(1, top + 1)

    # weights[j] = weight of piece j (declared output)
    weights = [pulp.LpVariable(f"weights_{j}", 1, top, cat="Integer") for j in range(n)]

    # the pieces add up to the original weight
    problem += pulp.lpSum(weights) == m

    # Pieces of equal weight are interchangeable, so what matters for weighing is
    # how many pieces there are of each weight: count[v] = number of pieces that
    # weigh v pounds. The pieces listed in `weights` are these counts, laid out in
    # positions: is_weight[j][v] = 1 if piece j weighs v.
    is_weight = [{v: pulp.LpVariable(f"is_weight_{j}_{v}", cat="Binary") for v in values}
                 for j in range(n)]
    count = {v: pulp.LpVariable(f"count_{v}", 0, n, cat="Integer") for v in values}
    for j in range(n):
        problem += pulp.lpSum(is_weight[j].values()) == 1
        problem += weights[j] == pulp.lpSum(v * var for v, var in is_weight[j].items())
    for v in values:
        problem += count[v] == pulp.lpSum(is_weight[j][v] for j in range(n))

    # Every weight t = 1..m can be weighed. net[t][v] = (pieces of weight v on the
    # far pan) - (pieces of weight v on the object's pan). Pieces of weight v on
    # opposite pans would cancel, so any net number between -count[v] and
    # +count[v] can be arranged, and the pans balance when the net pounds add up to t.
    for t in range(1, m + 1):
        net = {v: pulp.LpVariable(f"net_{t}_{v}", -n, n, cat="Integer") for v in values}
        for v in values:
            problem += net[v] <= count[v]
            problem += net[v] >= -count[v]
        problem += pulp.lpSum(v * net[v] for v in values) == t

    return problem, {"weights": weights}
