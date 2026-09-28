"""Equal-sized groups: split a sorted list into k groups at k - 1 break points, keeping equal values together, with sizes as close to n / k as possible."""
from docplex.mp.model import Model


def build(instance):
    a, k = instance["a"], instance["k"]
    n = len(a)
    ideal = round(n / k)  # the ideal group size, rounded as Python rounds, like the reference
    breaks = range(k - 1)

    # A break point j (1-based: the first j elements lie before it) may not
    # separate two equal values, so it can only sit where the value changes.
    # The reference also leaves j = n unconstrained.
    allowed = [j for j in range(1, n) if a[j - 1] != a[j]] + [n]

    model = Model("equal_sized_groups")

    # at[p, j] is 1 when break point p is at position j. Choosing among the
    # allowed positions encodes "equal values stay in one group" directly,
    # instead of forbidding each of the many other positions one by one.
    at = model.binary_var_matrix(breaks, allowed, name="at")
    for p in breaks:
        model.add_constraint(model.sum(at[p, j] for j in allowed) == 1, ctname=f"one_position_{p}")
    x = [model.sum(j * at[p, j] for j in allowed) for p in breaks]

    # size[i] is the number of elements in group i, at least 1 as in the reference:
    # the first group ends at the first break point, each later one at the next,
    # and the last runs to the end of the list.
    size = model.integer_var_list(k, 1, n, name="size")
    model.add_constraint(size[0] == x[0], ctname="first_group")
    for i in range(1, k - 1):
        model.add_constraint(size[i] == x[i] - x[i - 1], ctname=f"group_{i}")
    model.add_constraint(size[k - 1] == n - x[k - 2], ctname="last_group")

    # error[i] is at least the distance of group i's size from the ideal size;
    # since the total is minimised, each is exactly that distance at the optimum.
    error = model.integer_var_list(k, 0, n, name="error")
    for i in range(k):
        model.add_constraint(error[i] >= size[i] - ideal, ctname=f"over_{i}")
        model.add_constraint(error[i] >= ideal - size[i], ctname=f"under_{i}")

    # The total error, which the reference bounds to 0..n, is minimised.
    total_error = model.sum(error)
    model.add_constraint(total_error <= n, ctname="error_domain")
    model.minimize(total_error)

    return model, {"x": x}
