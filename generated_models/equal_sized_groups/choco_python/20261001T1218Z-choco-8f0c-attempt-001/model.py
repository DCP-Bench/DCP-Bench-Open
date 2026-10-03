# Equal sized groups: split a sorted list of elements into k groups by choosing k - 1
# break points, so that the group sizes are as close as possible to round(n / k) and
# equal values are never separated. Minimise the total deviation from the ideal size.
from pychoco.model import Model


def build(instance):
    a = instance["a"]  # the sorted elements to divide
    k = instance["k"]  # number of groups
    n = len(a)
    ideal_size = round(n / k)  # average group size, the target for every group

    # A break point x = j puts the first j elements before it, so it separates
    # a[j - 1] from a[j]. Equal values must stay in one group, hence a break point may only
    # sit between two different values.
    allowed_breaks = [j for j in range(1, n) if a[j - 1] != a[j]]

    model = Model()

    # x[p] = the 1-based index of the last element of group p (the p-th break point)
    x = [model.intvar(allowed_breaks, name=f"x_{p}") for p in range(k - 1)]
    # s[i] = size of group i; every group holds at least one element
    s = [model.intvar(1, n, name=f"s_{i}") for i in range(k)]

    # the size of each group is the difference between consecutive break points
    model.arithm(s[0], "=", x[0]).post()
    for i in range(1, k - 1):
        model.arithm(x[i], "-", x[i - 1], "=", s[i]).post()
    model.arithm(s[k - 1], "+", x[k - 2], "=", n).post()

    # deviation of each group size from the ideal size, in absolute value
    signed_error = [model.intvar(-n, n, name=f"signed_error_{i}") for i in range(k)]
    error = [model.intvar(0, n, name=f"error_{i}") for i in range(k)]
    for i in range(k):
        model.arithm(s[i], "-", ideal_size, "=", signed_error[i]).post()
        model.absolute(error[i], signed_error[i]).post()

    # total error, the quantity to minimise (its upper bound n is the problem's own)
    z = model.intvar(0, n, name="z")
    model.sum(error, "=", z).post()

    return model, {"x": x}, ("minimize", z)
