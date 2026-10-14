# Covering: select a set of workers so that every task has at least one selected qualified worker, minimising the total hiring cost.
from pycsp3 import *

cost = data.Cost
nb_workers = data.nb_workers
num_tasks = data.num_tasks
qualified = data.Qualified

# workers[w] = 1 if worker w (0-indexed) is hired
workers = VarArray(size=nb_workers, dom={0, 1})
# total_cost is the sum of the hiring costs of the hired workers
total_cost = Var(dom=range(sum(cost) + 1))

satisfy(
    # every task must be performed by at least one hired worker who is qualified for it
    [Sum(workers[w - 1] for w in qualified[t]) >= 1 for t in range(num_tasks)],
    # the total cost is the sum of the costs of the hired workers
    total_cost == Sum(cost[w] * workers[w] for w in range(nb_workers)),
)

# minimise the total hiring cost
minimize(total_cost)
