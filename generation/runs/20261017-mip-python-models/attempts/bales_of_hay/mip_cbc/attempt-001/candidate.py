# Bales of hay: n bales with unknown integer weights. The bales were weighed in all
# possible combinations of two, and the n(n-1)/2 pair weights were listed in numerical
# order without saying which pair gave which weight. Find the weight of each bale.
import mip


def build(instance):
    n = instance["n"]
    weights = instance["weights"]
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    m = len(pairs)

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # bale weights are integers. Bounds come from the data: for three or more bales,
    # bale i = (pair(i,j) + pair(i,k) - pair(j,k)) / 2, and every pair weight lies
    # between the smallest and the largest given weight.
    wmin = min(weights)
    wmax = max(weights)
    lo = (2 * wmin - wmax) // 2
    hi = (2 * wmax - wmin) // 2
    bales = [model.add_var(f"bale_{i}", lb=lo, ub=hi, var_type=mip.INTEGER) for i in range(n)]

    # each pair of bales is weighed once: assign each pair one entry of the list.
    # assign[p][k] = 1 when pair p is the k-th weight in the list.
    assign = [[model.add_var(f"assign_{p}_{k}", var_type=mip.BINARY) for k in range(m)]
              for p in range(m)]

    # every pair of bales has exactly one weight in the list
    for p in range(m):
        model += mip.xsum(assign[p][k] for k in range(m)) == 1

    # every weight in the list belongs to exactly one pair of bales
    for k in range(m):
        model += mip.xsum(assign[p][k] for p in range(m)) == 1

    # the weight of a pair of bales is the sum of the two bale weights
    for p, (i, j) in enumerate(pairs):
        model += bales[i] + bales[j] == mip.xsum(weights[k] * assign[p][k] for k in range(m))

    return model, {"bales": bales}
