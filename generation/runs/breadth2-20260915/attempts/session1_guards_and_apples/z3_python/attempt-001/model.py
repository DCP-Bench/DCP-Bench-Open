import z3


def build(instance):
    gates = instance["num_gates"]
    apples = [z3.Int(f"apples_{i}") for i in range(gates + 1)]
    constraints = [a >= 0 for a in apples] + [a <= 100 for a in apples]
    constraints.append(apples[gates] == 1)
    for i in range(1, gates + 1):
        constraints.append(apples[i - 1] == 2 * (apples[i] + 1))
    return constraints, {"apples": apples}
