# Assign every task to a distinct person at least total cost.
from dcp_maxsat import MaxSat


def build(instance):
    cost = instance["cost"]
    rows, cols = len(cost), len(cost[0])

    sat = MaxSat()
    x = sat.bool_grid(rows, cols)
    for i in range(rows):
        sat.exactly(x[i], 1)
    for j in range(cols):
        sat.at_most([x[i][j] for i in range(rows)], 1)

    # One choice per row, so the total lies between the row minima and maxima.
    floor = sum(min(row) for row in cost)
    ceiling = sum(max(row) for row in cost)
    total = sat.int(floor, ceiling)
    flat_weights = [cost[i][j] for i in range(rows) for j in range(cols)]
    flat_lits = [x[i][j] for i in range(rows) for j in range(cols)]
    sat.link_bool_sum(flat_weights, flat_lits, total)
    return sat, {"x": x}, ("minimize", total)
