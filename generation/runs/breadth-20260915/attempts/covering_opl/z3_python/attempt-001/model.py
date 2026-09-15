import z3


def build(instance):
    count, qualified, cost = instance["nb_workers"], instance["Qualified"], instance["Cost"]
    hired = [z3.Bool(f"w_{i}") for i in range(count)]
    picked = [z3.If(hired[i], 1, 0) for i in range(count)]
    total = z3.Int("total_cost")
    constraints = [total == z3.Sum([cost[i] * picked[i] for i in range(count)]),
                   total >= 0, total <= count * sum(cost)]
    for task in qualified:
        constraints.append(z3.Sum([picked[worker - 1] for worker in task]) >= 1)
    return constraints, {"total_cost": total, "workers": hired}, ("minimize", total)
