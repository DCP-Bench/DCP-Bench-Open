# Equal-sized groups: cut a sorted list of N elements into K groups, with equal values kept together,
# so that the total deviation of each group's size from round(N/K) is minimised. Output: the K-1 break points.
from pyscipopt import Model, quicksum


def build(instance):
    # the sorted list and the number of groups come from the instance
    a = instance["a"]
    K = instance["k"]
    N = len(a)
    # the ideal group size (problem statement: close to round(N/K))
    target = round(N / K)

    # a break point is 1-based position p, meaning the group ends at element p.
    # Only positions where the value changes can be break points, so equal values stay together.
    # This set is derived from the sorted list in the instance.
    cuts = [p for p in range(1, N) if a[p - 1] != a[p]]

    m = Model()

    # one-hot choice: b[j, p] = 1 if break point j is at position p
    b = {(j, p): m.addVar(name=f"b_{j}_{p}", vtype="B") for j in range(K - 1) for p in cuts}

    # break point j is exactly one of the allowed cut positions
    x = [quicksum(p * b[j, p] for p in cuts) for j in range(K - 1)]
    for j in range(K - 1):
        # each break point is at exactly one position
        m.addCons(quicksum(b[j, p] for p in cuts) == 1)

    # break points are strictly increasing, so every group is non-empty
    for j in range(K - 2):
        # break point j comes before break point j+1
        m.addCons(x[j] + 1 <= x[j + 1])

    # group boundaries: the first group starts at 0 and the last group ends at N
    bounds = [0] + x + [N]

    # deviation of each group size from the target, as two linear inequalities for the absolute value
    dev = [m.addVar(name=f"dev_{g}", vtype="I", lb=0, ub=N) for g in range(K)]
    for g in range(K):
        # group g has size bounds[g+1] - bounds[g]
        size = bounds[g + 1] - bounds[g]
        # error = |size - target|
        m.addCons(dev[g] >= size - target)
        m.addCons(dev[g] >= target - size)

    # the total error of all groups is minimised
    m.setObjective(quicksum(dev), "minimize")

    # the output: the K-1 break points, 1-based
    return m, {"x": x}
