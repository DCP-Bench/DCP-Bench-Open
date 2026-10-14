"""Hanging weights: thirteen different weights A..M, each an integer 1..13, hang from a
system of bars; at every pivot the weights on either side, multiplied by their distances,
balance, and a hanging bar counts as one weight equal to its total.

The model reports the weights a..m.
"""
import pulp


def build(instance):
    del instance  # the puzzle has no instance data

    names = "abcdefghijklm"
    n = 13
    values = range(1, n + 1)

    problem = pulp.LpProblem("hanging_weights", pulp.LpMinimize)  # satisfaction

    # weight[w][v] = 1 if weight w is v; all weights differ, so this is a one-to-one
    # matching of the 13 weights to the values 1..13
    weight = {w: [pulp.LpVariable(f"weight_{w}_{v}", cat="Binary") for v in values] for w in names}
    for w in names:
        problem += pulp.lpSum(weight[w]) == 1
    for k in range(n):
        problem += pulp.lpSum(weight[w][k] for w in names) == 1
    a, b, c, d, e, f, g, h, i, j, k, l, m = (pulp.lpSum(v * var for v, var in zip(values, weight[w]))
                                             for w in names)

    # the balance of each bar, from the diagram
    problem += 4 * a == b                                         # bar A-B
    problem += 5 * c == d                                         # bar C-D
    problem += 3 * e == 2 * f                                     # bar E-F
    problem += 3 * g == 2 * (c + d)                               # bar G-(C,D)
    problem += 3 * (a + b) + 2 * j == k + 2 * (g + c + d)         # bar J-K with A-B and G
    problem += 3 * h == 2 * (e + f) + 3 * i                       # bar H-I with E-F
    problem += h + i + e + f == l + 4 * m                         # bar L-M with H's bar
    problem += 4 * (l + m + h + i + e + f) == 3 * (j + k + g + a + b + c + d)  # top bar

    return problem, dict(zip(names, (a, b, c, d, e, f, g, h, i, j, k, l, m)))
