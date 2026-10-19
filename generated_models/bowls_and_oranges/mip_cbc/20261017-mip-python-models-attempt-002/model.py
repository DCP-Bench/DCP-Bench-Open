# Bowls and oranges: place all m oranges in n bowls set in a line at 1 metre intervals,
# no more than one orange per bowl, so that there are no three oranges A, B, C with
# distance(A, B) equal to distance(B, C). Output x lists the bowls holding the oranges,
# in ascending order. Bowls are numbered from 1 to n, as in the description's line of bowls.
import mip


def build(instance):
    n = instance["n"]  # number of bowls, from the instance
    m = instance["m"]  # number of oranges, from the instance

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # y[k][j] = 1 if orange k is placed in bowl j+1 (bowl numbers run 1..n)
    y = [[model.add_var(f"y_{k}_{j}", var_type=mip.BINARY) for j in range(n)]
         for k in range(m)]
    # x[k] = the bowl number of orange k; the oranges are numbered in ascending bowl order
    x = [model.add_var(f"x_{k}", lb=1, ub=n, var_type=mip.INTEGER)
         for k in range(m)]
    # occ[j] = 1 if bowl j+1 holds an orange
    occ = [mip.xsum(y[k][j] for k in range(m)) for j in range(n)]

    # place all oranges: every orange is in exactly one bowl
    for k in range(m):
        model += mip.xsum(y[k]) == 1
        # the bowl number of orange k is the bowl it sits in
        model += x[k] == mip.xsum((j + 1) * y[k][j] for j in range(n))

    # no more than one orange in each bowl
    for j in range(n):
        model += occ[j] <= 1

    # the output lists the bowls in ascending order
    for k in range(m - 1):
        model += x[k] + 1 <= x[k + 1]

    # no three oranges A, B, C with distance(A, B) equal to distance(B, C):
    # for bowls i < i + d < i + 2d, at most two of the three bowls hold an orange
    for i in range(n):
        for d in range(1, n):
            if i + 2 * d > n - 1:
                break
            model += occ[i] + occ[i + d] + occ[i + 2 * d] <= 2

    # satisfaction problem: no objective
    return model, {"x": x}
