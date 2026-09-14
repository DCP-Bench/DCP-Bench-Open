import itertools

from ortools.sat.python import cp_model


def build(instance):
    n = instance["n"]
    n_sets = n * (n - 1) // 6
    model = cp_model.CpModel()
    sets = [[model.new_bool_var(f"sets_{i}_{j}") for j in range(n)] for i in range(n_sets)]
    for row in sets:
        # Every triple holds three elements.
        model.add(sum(row) == 3)
    for i1, i2 in itertools.combinations(range(n_sets), 2):
        # Two triples share at most one element.
        shared = []
        for j in range(n):
            both = model.new_bool_var(f"shared_{i1}_{i2}_{j}")
            model.add_bool_and(sets[i1][j], sets[i2][j]).only_enforce_if(both)
            model.add_bool_or(~sets[i1][j], ~sets[i2][j]).only_enforce_if(~both)
            shared.append(both)
        model.add(sum(shared) <= 1)
    return model, {"sets": sets}
