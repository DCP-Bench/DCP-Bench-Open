from ortools.sat.python import cp_model


def build(instance):
    amount, types, available = (instance["amount"], instance["types_of_coins"],
                                instance["available_coins"])
    n = len(types)
    model = cp_model.CpModel()
    counts = [model.new_int_var(0, max(available), f"c_{i}") for i in range(n)]
    model.add(sum(counts[i] * types[i] for i in range(n)) == amount)
    for i in range(n):
        model.add(counts[i] <= available[i])
    model.minimize(sum(counts))
    return model, {"coin_counts": counts}
