import cpmpy as cp


def build(instance):
    count, compatible = instance["num_people"], instance["compatible"]
    donates = cp.boolvar(shape=(count, count), name="transplants")
    model = cp.Model()
    for i in range(count):
        gives = cp.sum([donates[i, j] for j in range(count)])
        receives = cp.sum([donates[k, i] for k in range(count)])
        model += gives <= 1
        model += receives <= 1
        # Anyone who gives a kidney must receive one; both sums are 0 or 1 above.
        model += gives <= receives
        for j in range(count):
            if j + 1 not in compatible[i]:
                model += donates[i, j] == 0
    model.maximize(cp.sum([donates[i, j] for i in range(count) for j in range(count)]))
    return model, {"transplants": [[donates[i, j] for j in range(count)] for i in range(count)]}
