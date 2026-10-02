"""Bowls and oranges: bowls stand in a line one meter apart, numbered 1..n.
Put m oranges into distinct bowls so that no three oranges A, B, C have the
distance from A to B equal to the distance from B to C.

x lists the bowls holding the oranges in ascending order.
"""
import pulp


def build(instance):
    n = instance["n"]  # number of bowls
    m = instance["m"]  # number of oranges

    problem = pulp.LpProblem("bowls_and_oranges", pulp.LpMinimize)

    # The oranges are listed in ascending bowl order, so the k-th orange (k = 0..m-1)
    # lies in a bowl with k bowls below it and m-1-k bowls above it: its bowl is
    # between k+1 and n-(m-1-k).
    low = [k + 1 for k in range(m)]
    high = [n - (m - 1 - k) for k in range(m)]

    # in_bowl[k][b] = 1 if the k-th orange is in bowl b
    in_bowl = [{b: pulp.LpVariable(f"in_bowl_{k}_{b}", cat="Binary")
                for b in range(low[k], high[k] + 1)} for k in range(m)]

    # x[k] = the bowl of the k-th orange (declared output), a bounded integer
    # tied to the 0/1 variables by equality
    x = [pulp.LpVariable(f"x_{k}", low[k], high[k], cat="Integer") for k in range(m)]

    # every orange is in exactly one bowl, and x reads it back
    for k in range(m):
        problem += pulp.lpSum(in_bowl[k].values()) == 1
        problem += x[k] == pulp.lpSum(b * var for b, var in in_bowl[k].items())

    # the bowls of consecutive oranges strictly increase: ascending order, and
    # no bowl holds more than one orange
    for k in range(m - 1):
        problem += x[k + 1] >= x[k] + 1

    # occupied[b] = 1 if some orange is in bowl b
    occupied = {b: pulp.lpSum(in_bowl[k][b] for k in range(m) if b in in_bowl[k])
                for b in range(1, n + 1)}

    # no three oranges A, B, C with the distance A to B equal to B to C: for every
    # three bowls b, b + d, b + 2d at most two are occupied
    for first in range(1, n + 1):
        for gap in range(1, (n - first) // 2 + 1):
            problem += (occupied[first] + occupied[first + gap]
                        + occupied[first + 2 * gap]) <= 2

    return problem, {"x": x}
