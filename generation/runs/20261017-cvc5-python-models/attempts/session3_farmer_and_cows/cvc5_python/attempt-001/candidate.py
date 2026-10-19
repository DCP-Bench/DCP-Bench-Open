# Farmer and cows: distribute cows 1..num_cows among num_sons sons so that
# each son gets the prescribed number of cows (cows_per_son) and every son
# receives the same total quantity of milk (a cow's milk equals its number).
import cvc5.pythonic as cz


def build(instance):
    n = instance["num_cows"]
    s_count = instance["num_sons"]
    cows_per_son = instance["cows_per_son"]

    # x[i] is the son (0-based) that receives cow i+1.
    x = [cz.Int(f"x_{i}") for i in range(n)]

    constraints = []

    # Each cow goes to exactly one son, so its value is a son index.
    # cvc5 integers are unbounded: bound them to the son range.
    for i in range(n):
        constraints.append(x[i] >= 0)
        constraints.append(x[i] <= s_count - 1)

    # The farmer has a number of sons and wants to distribute his cows to them
    # according to a given distribution: son s receives cows_per_son[s] cows.
    for s in range(s_count):
        constraints.append(
            cz.Sum([cz.If(x[i] == s, 1, 0) for i in range(n)]) == cows_per_son[s]
        )

    # The total quantity of milk produced should be the same for each son.
    # The milk of a son is the sum of the numbers of its cows.
    milk = [
        cz.Sum([cz.If(x[i] == s, i + 1, 0) for i in range(n)])
        for s in range(s_count)
    ]
    for s in range(1, s_count):
        constraints.append(milk[s] == milk[0])

    outputs = {"cow_assignments": x}
    return constraints, outputs
