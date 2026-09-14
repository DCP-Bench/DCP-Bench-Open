# bin_packing
Instance: `weights`, `capacity`, `num_bins`. Output: `bins` — the bin of each
item, 0..num_bins-1. The reference writes the capacity constraint for each
i in range(len(weights)), which is what this model mirrors: for a bin index
beyond num_bins the sum is empty and the constraint is vacuous.
An assignment matrix carries the reified `bins[j] == i` that MIP cannot state.
