from paramita.modelling import Bool, If


# All-interval series of size n (CSPLib prob007): a permutation of the pitch
# classes 0..n-1 whose neighbour intervals are a permutation of 1..n-1.
def build(instance):
    n = instance["n"]

    # x[i][v] = 1 if position i holds pitch class v (one-hot over v)
    x = [[Bool(f"x_{i}_{v}") for v in range(n)] for i in range(n)]
    # d[k][t] = 1 if the interval between positions k and k+1 is t+1 (one-hot over t)
    d = [[Bool(f"d_{k}_{t}") for t in range(n - 1)] for k in range(n - 1)]

    cons = []

    # each pitch class occurs exactly once in the series
    cons += [sum(x[i]) == 1 for i in range(n)]
    cons += [sum(x[i][v] for i in range(n)) == 1 for v in range(n)]

    # the interval between two neighbouring notes is the distance between their pitch classes
    cons += [sum(d[k]) == 1 for k in range(n - 1)]
    for k in range(n - 1):
        for a in range(n):
            for b in range(n):
                if a != b:
                    cons.append(If(x[k][a] & x[k + 1][b], d[k][abs(a - b) - 1]))

    # the intervals cover the full set from 1 to n-1 (each exactly once)
    cons += [sum(d[k][t] for k in range(n - 1)) == 1 for t in range(n - 1)]

    pitch = [sum(v * x[i][v] for v in range(n)) for i in range(n)]
    diffs = [sum((t + 1) * d[k][t] for t in range(n - 1)) for k in range(n - 1)]
    return cons, {"x": pitch, "diffs": diffs}
