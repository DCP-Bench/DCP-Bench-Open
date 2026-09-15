import cpmpy as cp


def build(instance):
    count, qualified, cost = instance["nb_workers"], instance["Qualified"], instance["Cost"]
    hired = cp.boolvar(shape=count, name="workers")
    total = cp.intvar(0, count * sum(cost), name="total_cost")
    model = cp.Model(total == cp.sum([cost[i] * hired[i] for i in range(count)]))
    for task in qualified:
        # The instance lists qualified workers 1-based.
        model += cp.sum([hired[worker - 1] for worker in task]) >= 1
    model.minimize(total)
    return model, {"total_cost": total, "workers": [hired[i] for i in range(count)]}
