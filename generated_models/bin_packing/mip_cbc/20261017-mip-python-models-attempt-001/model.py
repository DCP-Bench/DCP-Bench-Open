# Bin packing: assign each item to one of num_bins bins of a fixed capacity so
# that the total weight of the items in each bin does not exceed the capacity.
# Output bins[i] is the 0-indexed bin that item i is assigned to. Satisfaction.
import mip


def build(instance):
    weights = instance["weights"]
    capacity = instance["capacity"]
    num_bins = instance["num_bins"]
    n = len(weights)

    m = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # x[i][b] = 1 when item i is assigned to bin b.
    x = [[m.add_var(f"x_{i}_{b}", var_type=mip.BINARY) for b in range(num_bins)]
         for i in range(n)]
    # bins[i] is the bin number of item i, tied to its binaries below.
    bins = [m.add_var(f"bins_{i}", lb=0, ub=num_bins - 1, var_type=mip.INTEGER)
            for i in range(n)]

    # assign each item to exactly one bin
    for i in range(n):
        m += mip.xsum(x[i][b] for b in range(num_bins)) == 1

    # the total weight of the items in each bin does not exceed the capacity
    for b in range(num_bins):
        m += mip.xsum(weights[i] * x[i][b] for i in range(n)) <= capacity

    # the bin of each item is the bin its binary marks
    for i in range(n):
        m += bins[i] == mip.xsum(b * x[i][b] for b in range(num_bins))

    return m, {"bins": bins}
