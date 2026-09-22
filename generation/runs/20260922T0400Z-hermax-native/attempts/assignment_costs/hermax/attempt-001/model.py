# Assign every task to a distinct person at least total cost.
from hermax.model import Model


def build(instance):
    cost = instance["cost"]
    rows, cols = len(cost), len(cost[0])

    m = Model()
    x = m.bool_matrix("x", rows, cols)
    for i in range(rows):
        m &= x.row(i).exactly_one()
    for j in range(cols):
        m &= x.col(j).at_most_one()

    # Minimising: the soft clause is broken by *using* a pairing, so it pays
    # that pairing's cost. The total broken weight is the assignment's cost.
    for i in range(rows):
        for j in range(cols):
            m.obj[cost[i][j]] += ~x[i][j]
    return m, {"x": x}
