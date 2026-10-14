# Bin packing: assign each item to one of num_bins bins so that no bin holds more than the capacity.
from pycsp3 import *

weights = data.weights
capacity = data.capacity
num_bins = data.num_bins
n = len(weights)

# bins[i] is the 0-indexed bin that item i is assigned to
bins = VarArray(size=n, dom=range(num_bins))

satisfy(
    # the total weight of the items in each bin must not exceed the capacity
    BinPacking(bins, sizes=weights, limits=[capacity] * num_bins),
)
