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
    # so a piece is at most m - (n - 1) pounds. This is the largest value the
    # sum constraint below allows, and it is the big-M of the products.
    top = m - (n - 1)

    # weights[j] = weight of piece j (declared output)
    weights = [pulp.LpVariable(f"weights_{j}", 1, top, cat="Integer") for j in range(n)]

    # the pieces add up to the original weight
    problem += pulp.lpSum(weights) == m

    # Every weight t = 1..m can be weighed: choose for each piece whether it goes on
    # the object's pan (sign -1), the other pan (sign +1) or is left off (sign 0), so
    # that the signed sum of the pieces is t.
    for t in range(1, m + 1):
        signed = []
        for j in range(n):
            # plus / minus = 1 if piece j goes on the + / - side for target t
            plus = pulp.LpVariable(f"plus_{t}_{j}", cat="Binary")
            minus = pulp.LpVariable(f"minus_{t}_{j}", cat="Binary")
            problem += plus + minus <= 1  # a piece is on at most one side

            # The product sign * weight is not linear, so it is split into the
            # piece's weight when it is on the + side (used_plus) and on the -
            # side (used_minus). Each equals the weight when its indicator is 1
            # and 0 otherwise.
            used_plus = pulp.LpVariable(f"used_plus_{t}_{j}", 0, top)
            used_minus = pulp.LpVariable(f"used_minus_{t}_{j}", 0, top)
            for used, side in ((used_plus, plus), (used_minus, minus)):
                problem += used <= top * side
                problem += used <= weights[j]
                problem += used >= weights[j] - top * (1 - side)
            signed.append(used_plus - used_minus)

        problem += pulp.lpSum(signed) == t

    return problem, {"weights": weights}
