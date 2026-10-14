Find the closest combination of packs of different sizes that meets or exceeds the target.
  -> counts[i] is the number of packs of size packs[i]; IntVarArray(*this, 2, 0, target/packs[i] + 1) (an optimal solution never uses more than ceil(target/packs[i]) packs of one size)
Print the counts of each pack size used (counts).
  -> output("counts", counts)
the total number of items in the combination meets or exceeds the target
  -> total = expr(*this, packs[0]*counts[0] + packs[1]*counts[1]); rel(*this, total >= target)
closest = smallest total that meets the target (minimise the excess over the target)
  -> minimize(total)
branching: packs counts from the smallest count first
  -> branch(*this, counts, INT_VAR_SIZE_MIN(), INT_VAL_MIN())
