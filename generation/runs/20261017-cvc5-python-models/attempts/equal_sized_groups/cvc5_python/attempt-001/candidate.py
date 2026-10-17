# Problem: equal_sized_groups
# Divide a sorted list of N elements into K groups by choosing K-1 split points between
# them. Equal values must stay in the same group. Make the groups as close in size as
# possible to round(N/K). Output x: the 1-based index of the last element of each of the
# first K-1 groups, minimising the total absolute error of the group sizes.
import cvc5.pythonic as cz


def build(instance):
    a = instance["a"]
    n = len(a)
    k = instance["k"]
    target = round(n / k)

    # Split points are 1-based positions p with 1 <= p <= N-1, between element p and p+1.
    # The split is allowed only where the two neighbouring values differ.
    allowed = [p for p in range(1, n) if a[p - 1] != a[p]]

    x = [cz.Int(f"x_{j}") for j in range(k - 1)]
    constraints = []

    # The K-1 split points are strictly increasing, so every group is non-empty.
    constraints.append(x[0] >= 1)
    for j in range(1, k - 1):
        constraints.append(x[j - 1] < x[j])
    constraints.append(x[-1] <= n - 1)

    # Each split point lies between two elements of different value, so equal values
    # are never separated.
    for xj in x:
        options = [xj == p for p in allowed]
        if not options:
            constraints.append(cz.BoolVal(False))
        elif len(options) == 1:
            constraints.append(options[0])
        else:
            constraints.append(cz.Or(options))

    # Group sizes: the difference of consecutive break points, with 0 and N as the ends.
    bounds = [0] + x + [n]
    errors = []
    for j in range(k):
        size = bounds[j + 1] - bounds[j]
        errors.append(cz.If(size >= target, size - target, target - size))

    # Objective: total absolute error of the group sizes against round(N/K).
    total = errors[0]
    for e in errors[1:]:
        total = total + e

    return constraints, {"x": x}, ("minimize", total)
