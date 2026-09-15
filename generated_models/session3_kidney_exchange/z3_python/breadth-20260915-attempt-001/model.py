import z3


def build(instance):
    count, compatible = instance["num_people"], instance["compatible"]
    donates = [[z3.Bool(f"t_{i}_{j}") for j in range(count)] for i in range(count)]
    picked = [[z3.If(donates[i][j], 1, 0) for j in range(count)] for i in range(count)]
    constraints = []
    for i in range(count):
        gives = z3.Sum(picked[i])
        receives = z3.Sum([picked[k][i] for k in range(count)])
        constraints += [gives <= 1, receives <= 1, gives <= receives]
        for j in range(count):
            if j + 1 not in compatible[i]:
                constraints.append(z3.Not(donates[i][j]))
    objective = z3.Sum([picked[i][j] for i in range(count) for j in range(count)])
    return constraints, {"transplants": donates}, ("maximize", objective)
