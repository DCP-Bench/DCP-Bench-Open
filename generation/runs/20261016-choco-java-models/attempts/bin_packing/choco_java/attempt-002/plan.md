# Plan: bin_packing (bins[i] = bin of item i, 0-indexed)

- "assign each item to a bin" -> bins[i] in 0..num_bins-1 (`m.intVarArray("bins", n, 0, numBins-1)`)
- "the total weight of the items in each bin does not exceed the capacity" -> load[j] = total weight in bin j, load[j] <= capacity (`m.binPacking(bins, weights, load, 0)`)
- implied: the loads add up to the total weight of all items -> `m.sum(load, "=", total)`
- search: branch on the bins, first-fail with largest weight first; Luby restarts
- "Print the bin each item is assigned to (bins)" -> output bins
- Objective: none (satisfaction)
