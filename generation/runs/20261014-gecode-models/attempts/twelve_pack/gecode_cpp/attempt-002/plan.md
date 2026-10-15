Given a target number of items, find the closest combination of packs of different sizes that meets or exceeds the target.
  -> counts[i] in 0..target/packs[i]+1 (an optimal count never exceeds ceil(target/size)); IntVarArray(*this, n, 0, bound_i)
Print the counts of each pack size used (counts), one entry per pack size in the instance.
  -> output("counts", counts) over the array of size packs.size(), read from the instance
Total items bought is the sum of pack size times pack count, over every pack size.
  -> total = expr(*this, sum(IntArgs(packs), IntVarArgs(counts))) (linear over all pack sizes, not only packs[0] and packs[1])
The combination must meet or exceed the target.
  -> rel(*this, total, IRT_GQ, target)
Closest: fewest items above the target.
  -> minimize(total) (objective minimize, on total)
Branching: counts fixed first, fewest packs first.
  -> branch(*this, counts, INT_VAR_SIZE_MIN(), INT_VAL_MIN()); total is then fixed by bounds propagation of the linear sum
