"""Covering: hire the cheapest set of workers such that every task has a qualified worker."""
from docplex.mp.model import Model


def build(instance):
    cost = instance["Cost"]
    qualified = instance["Qualified"]  # qualified[t]: the workers, 1-based, who can do task t
    tasks = range(instance["num_tasks"])

    model = Model("covering_opl")

    # hire[w] is 1 when worker w is hired.
    hire = model.binary_var_list(instance["nb_workers"], name="workers")

    # Every task has at least one hired worker qualified for it (the list is 1-based).
    for t in tasks:
        model.add_constraint(model.sum(hire[w - 1] for w in qualified[t]) >= 1, ctname=f"task_{t}")

    # Minimise the total hiring cost.
    total_cost = model.dot(hire, cost)
    model.minimize(total_cost)

    return model, {"total_cost": total_cost, "workers": hire}
