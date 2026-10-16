# Plan: bin_packing, attempt 001

Problem: items with weights, bins of a fixed capacity, assign each item to one bin, total weight per bin <= capacity. Output bin index per item (0-indexed).

- each item is in exactly one bin -> one-hot Bools x_i_b, sum over b == 1 per item
- item bin index = sum(b * x_i_b) (integer expression, output bins)
- each bin's total weight <= capacity -> sum(w_i * x_i_b over i) <= capacity per bin b
- symmetry breaking (bins are interchangeable): bins numbered by first item, so item i uses bin <= i
- objective: none (satisfaction)
