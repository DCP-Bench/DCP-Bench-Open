from ortools.sat.python import cp_model


def build(instance):
    count, compatible = instance["num_people"], instance["compatible"]
    model = cp_model.CpModel()
    donates = [[model.new_bool_var(f"t_{i}_{j}") for j in range(count)] for i in range(count)]
    for i in range(count):
        gives = sum(donates[i])
        receives = sum(donates[k][i] for k in range(count))
        model.add(gives <= 1)
        model.add(receives <= 1)
        # Anyone who gives a kidney must receive one; both sums are 0 or 1 above.
        model.add(gives <= receives)
        for j in range(count):
            if j + 1 not in compatible[i]:
                model.add(donates[i][j] == 0)
    model.maximize(sum(donates[i][j] for i in range(count) for j in range(count)))
    return model, {"transplants": donates}
