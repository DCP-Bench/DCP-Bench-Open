# Covering: hire workers so that every task has at least one hired worker who
# is qualified for it, at the least total hiring cost.
from hermax.model import Model


def build(instance):
    nb_workers = instance["nb_workers"]
    qualified = instance["Qualified"]  # for each task, the workers (numbered from 1) who can do it
    cost = instance["Cost"]  # cost of hiring each worker

    m = Model()
    # workers[w] = worker w is hired
    workers = m.bool_vector("workers", nb_workers)

    # every task is done by at least one hired worker qualified for it
    for task in qualified:
        clause = workers[task[0] - 1]
        for w in task[1:]:
            clause = clause | workers[w - 1]
        m &= clause

    # Minimise the total cost: a hired worker pays their cost. A soft clause
    # pays when its literal is false, so the literal is "not hired".
    for w in range(nb_workers):
        m.obj[cost[w]] += ~workers[w]

    # total_cost is a declared output, so it is also an integer. Its bound is the
    # cost of hiring everybody, the largest total there can be, which keeps
    # the sum narrow; the objective itself is the soft clauses above.
    total_cost = m.int("total_cost", 0, sum(cost))
    m &= (sum(cost[w] * workers[w] for w in range(nb_workers)) == total_cost)

    return m, {"total_cost": total_cost, "workers": workers}
