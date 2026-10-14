Given several items of specific weights, assign each item to a bin -> bin = IntVarArray(n, 0, num_bins-1) (item i's bin, 0-indexed)
the total weight of the items in each bin does not exceed the capacity -> load = IntVarArray(num_bins, 0, capacity) with binpacking(*this, load, bin, sizes, IPL_DEF) [load_j = sum of weights of items in bin j]
a number of bins of a fixed capacity -> num_bins from the instance; bins are identical so value precedence breaks bin symmetry: precede(*this, bin, {0..num_bins-1})
print the bin each item is assigned to (bins) -> output("bins", bin)
branching -> branch on bin with INT_VAR_SIZE_MIN, INT_VAL_MIN
objective -> satisfaction, none
