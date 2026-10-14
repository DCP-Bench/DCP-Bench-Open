# Bin packing: assign each item to one of num_bins bins of a fixed capacity
# so that the items in each bin weigh no more than the capacity.

from pyscipopt import Model, quicksum

def build(instance):
    weights = instance["weights"]
    capacity = instance["capacity"]
    num_bins = instance["num_bins"]
    n = len(weights)

    m = Model()

    # y[i, b] = 1 if item i is put in bin b (one-hot choice of bin per item)
    y = {(i, b): m.addVar(name=f"y_{i}_{b}", vtype="B")
         for i in range(n) for b in range(num_bins)}

    # each item is assigned to exactly one bin
    for i in range(n):
        m.addCons(quicksum(y[i, b] for b in range(num_bins)) == 1)

    # the total weight of the items in each bin does not exceed the capacity
    for b in range(num_bins):
        m.addCons(quicksum(weights[i] * y[i, b] for i in range(n)) <= capacity)

    # bins[i] is the 0-indexed bin of item i
    bins = [quicksum(b * y[i, b] for b in range(num_bins)) for i in range(n)]
    return m, {"bins": bins}
