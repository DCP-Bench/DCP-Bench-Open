Bins are 0-indexed in the output, so the bins domain is int(0..num_bins-1) and the capacity check loops over bin values directly, using (bins[i] = b) * weights[i]. Accepted first try.
