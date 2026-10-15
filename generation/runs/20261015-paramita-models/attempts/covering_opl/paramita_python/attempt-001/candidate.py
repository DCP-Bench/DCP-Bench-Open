from paramita.modelling import Bool, Or

# Covering (set covering as an optimisation): choose a set of workers that
# performs every task, at minimum total hiring cost.
# Each worker i (1-based in the data) has a Bool "hired" and a hiring cost.
# Each task must be performed by at least one hired worker qualified for it.


def build(instance):
    n = instance["nb_workers"]
    cost = instance["Cost"]
    qualified = instance["Qualified"]

    hired = [Bool(f"hired_{i}") for i in range(n)]

    cons = []
    # every task is performed: at least one qualified worker is hired
    for t, workers in enumerate(qualified):
        cons.append(Or([hired[w - 1] for w in workers]))

    # total hiring cost of the selected workers
    total_cost = sum(cost[i] * hired[i] for i in range(n))

    return cons, {"total_cost": total_cost, "workers": hired}, ("minimize", total_cost)
