# Problem: equal_sized_groups. A sorted list of N elements is divided into K groups by
# K-1 break points (1-based index of the last element of each group, except the last group).
# Break points may only fall between two different values, so equal values stay together.
# Find K groups as close in size as possible to round(N/K). Minimise the total absolute
# deviation of the group sizes from that size. Output x: the 1-based break points, increasing.
import mip


def build(instance):
    a = instance["a"]
    k = instance["k"]
    n = len(a)
    target = round(n / k)

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # A break point at position p (1-based) lies between element p and element p+1.
    # It is allowed only where the two values differ.
    valid = [p for p in range(1, n) if a[p - 1] != a[p]]

    # Break point x_i is the position chosen by one binary z[i, p] per allowed position p.
    # One position per break point, and at most one break point per position.
    # Break points are integers, tied to their binaries by an equality row.
    x = []
    z = {}
    for i in range(k - 1):
        xi = model.add_var(f"x_{i}", lb=1, ub=n - 1, var_type=mip.INTEGER)
        x.append(xi)
        for p in valid:
            z[i, p] = model.add_var(f"z_{i}_{p}", var_type=mip.BINARY)
        model.add_constr(mip.xsum(z[i, p] for p in valid) == 1)
        model.add_constr(xi == mip.xsum(p * z[i, p] for p in valid))
    for p in valid:
        model.add_constr(mip.xsum(z[i, p] for i in range(k - 1)) <= 1)

    # The K-1 split points are in increasing order.
    for i in range(k - 2):
        model.add_constr(x[i] + 1 <= x[i + 1])

    # Group sizes from the break points: group j runs from bounds[j] + 1 to bounds[j + 1].
    # Each group's error is the absolute deviation from round(N/K), linearised by two rows.
    bounds = [0] + x + [n]
    errors = []
    for j in range(k):
        size = bounds[j + 1] - bounds[j]
        e = model.add_var(f"e_{j}", lb=0, ub=n, var_type=mip.INTEGER)
        model.add_constr(e >= size - target)
        model.add_constr(e >= target - size)
        errors.append(e)

    # Total error is minimised.
    model.objective = mip.xsum(errors)

    return model, {"x": x}
