# Covering: hire a set of workers at minimum total cost so that every task has at
# least one hired worker who is qualified to perform it.
from pychoco.model import Model


def build(instance):
    nb_workers = instance["nb_workers"]
    num_tasks = instance["num_tasks"]
    qualified = instance["Qualified"]  # qualified[j] = the workers who can do task j (1-based)
    cost = instance["Cost"]  # cost[i] = cost of hiring worker i

    model = Model()

    # workers[i] = 1 if worker i is hired
    workers = [model.boolvar(name=f"workers_{i}") for i in range(nb_workers)]
    # total cost of hiring the workers
    total_cost = model.intvar(0, sum(cost), name="total_cost")

    # the total cost is the sum of the hiring costs of the hired workers
    model.scalar(workers, cost, "=", total_cost).post()

    # every task is performed: at least one of the workers qualified for it is hired
    # (the instance numbers workers from 1, so subtract 1)
    for j in range(num_tasks):
        model.sum([workers[c - 1] for c in qualified[j]], ">=", 1).post()

    # minimise the cost of hiring
    return model, {"total_cost": total_cost, "workers": workers}, ("minimize", total_cost)
