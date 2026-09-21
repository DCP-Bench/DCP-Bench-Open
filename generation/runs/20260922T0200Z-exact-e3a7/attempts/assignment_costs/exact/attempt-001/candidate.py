# Assign every task to a distinct person at least total cost.
from dcp_pb import Pb


def build(instance):
    cost = instance["cost"]
    rows, cols = len(cost), len(cost[0])

    pb = Pb()
    x = pb.bool_grid(rows, cols)
    for i in range(rows):
        pb.exactly(x[i], 1)
    for j in range(cols):
        pb.at_most([x[i][j] for i in range(rows)], 1)

    pb.minimise([(cost[i][j], x[i][j]) for i in range(rows) for j in range(cols)])
    return pb, {"x": x}
