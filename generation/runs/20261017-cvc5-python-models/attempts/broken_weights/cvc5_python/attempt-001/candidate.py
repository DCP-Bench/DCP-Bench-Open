# Broken weights: a merchant's measuring weight of m pounds broke into n pieces. Each
# piece weighs a whole number of pounds, and the pieces can be used on a balance scale
# to weigh every integral weight between 1 and m. Print the weights of the pieces.
import cvc5.pythonic as cz


def build(instance):
    m = instance["m"]
    n = instance["n"]

    constraints = []

    # Each piece weighs a whole number of pounds between 1 and m, chosen as one value
    # (one-hot Booleans, so the solver propagates on Booleans rather than on integers).
    X = [[cz.Bool(f"x_{k}_{a}") for a in range(1, m + 1)] for k in range(n)]
    w = [cz.Int(f"w_{k}") for k in range(n)]
    for k in range(n):
        constraints.append(cz.Sum([cz.If(X[k][a - 1], 1, 0) for a in range(1, m + 1)]) == 1)
        constraints.append(w[k] == cz.Sum([cz.If(X[k][a - 1], a, 0) for a in range(1, m + 1)]))

    # The pieces together make up the total weight of the broken measuring weight.
    constraints.append(cz.Sum(w) == m)

    # Every integral weight between 1 and m can be weighed on the balance scale.
    # reach[k][v] says the value v is the signed sum of the first k pieces, where each
    # piece is put on the object's side (+), on the other side (-), or left off (0).
    # Only the implication that a true reach needs a witness is asserted, which keeps
    # the encoding to one direction and each reach true only through a real choice.
    offset = m
    reach = [
        [cz.Bool(f"r_{k}_{v + offset}") for v in range(-m, m + 1)]
        for k in range(n + 1)
    ]
    for v in range(-m, m + 1):
        constraints.append(reach[0][v + offset] if v == 0 else cz.Not(reach[0][v + offset]))
    for k in range(1, n + 1):
        for v in range(-m, m + 1):
            # The first k pieces reach v only if the first k-1 pieces reach v, or piece k
            # on one side (its value a, reached from v - a) or the other (from v + a).
            options = [reach[k - 1][v + offset]]
            for a in range(1, m + 1):
                if -m <= v - a <= m:
                    options.append(cz.And(X[k - 1][a - 1], reach[k - 1][v - a + offset]))
                if -m <= v + a <= m:
                    options.append(cz.And(X[k - 1][a - 1], reach[k - 1][v + a + offset]))
            body = options[0] if len(options) == 1 else cz.Or(options)
            constraints.append(cz.Implies(reach[k][v + offset], body))

    # Every weight from 1 to m is reached by all n pieces.
    for t in range(1, m + 1):
        constraints.append(reach[n][t + offset])

    s = cz.SolverFor("QF_LIA")
    s.add(*constraints)
    return s, {"weights": w}
