# Farmer and cows: distribute cows 1..num_cows among num_sons sons so that
# each son gets the prescribed number of cows (cows_per_son) and every son
# receives the same total quantity of milk (a cow's milk equals its number).
import cvc5.pythonic as cz


def build(instance):
    n = instance["num_cows"]
    s_count = instance["num_sons"]
    cows_per_son = instance["cows_per_son"]

    # b[i][s] is true when cow i+1 goes to son s.
    b = [[cz.Bool(f"b_{i}_{s}") for s in range(s_count)] for i in range(n)]

    constraints = []

    # Each cow goes to exactly one son: at least one son, and no two sons.
    # Pairwise exclusion is used because cvc5 has no exactly-one helper.
    for i in range(n):
        constraints.append(cz.Or(b[i]))
        for s in range(s_count):
            for t in range(s + 1, s_count):
                constraints.append(cz.Not(cz.And(b[i][s], b[i][t])))

    # The farmer has a number of sons and wants to distribute his cows to them
    # according to a given distribution: son s receives cows_per_son[s] cows.
    for s in range(s_count):
        constraints.append(
            cz.Sum([cz.If(b[i][s], 1, 0) for i in range(n)]) == cows_per_son[s]
        )

    # The total quantity of milk produced should be the same for each son.
    # The total milk is the sum of 1..num_cows, so each son gets total / num_sons.
    total = n * (n + 1) // 2
    if total % s_count != 0:
        p = cz.Bool("no_equal_split")
        constraints.append(cz.And(p, cz.Not(p)))
    else:
        target = total // s_count
        for s in range(s_count):
            constraints.append(
                cz.Sum([cz.If(b[i][s], i + 1, 0) for i in range(n)]) == target
            )

    # The output is the son index of each cow (0-based), built from the Booleans.
    x = [
        cz.Sum([cz.If(b[i][s], s, 0) for s in range(s_count)])
        for i in range(n)
    ]
    outputs = {"cow_assignments": x}
    return constraints, outputs
