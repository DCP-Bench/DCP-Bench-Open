# Kidney exchange: n people on a waiting list; compatible[i] is the set of people i can donate to.
# Choose donations so that anyone who gives a kidney receives one, no person receives more than
# one kidney, and the number of people receiving a kidney is maximised.
# transplants[i][j] is 1 if person i donates to person j.
import cvc5.pythonic as cz


def build(instance):
    n = instance["num_people"]
    compatible = instance["compatible"]

    # Compatibility data is 1-based; the model uses 0-based indices.
    allowed = [set(d - 1 for d in compatible[i]) for i in range(n)]

    x = {}
    for i in range(n):
        for j in range(n):
            if j in allowed[i]:
                x[(i, j)] = cz.Bool(f"x_{i}_{j}")

    constraints = []

    # Each person i can donate only to people in compatible[i].
    # (Edges outside compatible[i] do not exist as variables and are reported as False.)

    # Anyone who gives a kidney must receive one, and no person receives more than one kidney.
    for i in range(n):
        out_terms = [cz.If(x[(i, j)], 1, 0) for j in range(n) if (i, j) in x]
        in_terms = [cz.If(x[(j, i)], 1, 0) for j in range(n) if (j, i) in x]
        if out_terms and in_terms:
            constraints.append(cz.Sum(out_terms) == cz.Sum(in_terms))
        elif out_terms:
            constraints.extend(cz.Not(x[(i, j)]) for j in range(n) if (i, j) in x)
        elif in_terms:
            constraints.extend(cz.Not(x[(j, i)]) for j in range(n) if (j, i) in x)
        if len(in_terms) >= 2:
            constraints.append(cz.Sum(in_terms) <= 1)
        if len(out_terms) >= 2:
            constraints.append(cz.Sum(out_terms) <= 1)

    # Maximise the number of people that receive a new kidney.
    all_terms = [cz.If(v, 1, 0) for v in x.values()]
    objective = cz.Sum(all_terms) if all_terms else 0

    transplants = [
        [x[(i, j)] if (i, j) in x else False for j in range(n)] for i in range(n)
    ]

    return constraints, {"transplants": transplants}, ("maximize", objective)
