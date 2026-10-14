Problem: minimise the number of coins x_i of each denomination d_i so that every amount a in 1..max-1 can be paid exactly.

- x_i counts coins of type i; each x_i is bounded by (max-1)/d_i, since a payment below max never uses more coins of one type than that -> IntVarArray domain 0..(max-1)/d_i
- "pay exactly any amount smaller than max" (for each amount a) -> per amount a, a payment vector p_a with p_a[i] coins of type i -> IntVarArray(*this, n, 0, min(a/d_i, (max-1)/d_i)) per amount (domain bound from the amount)
- "the amount is exactly paid" -> sum_i d_i * p_a[i] = a -> linear(*this, IntArgs(d), p_a, IRT_EQ, a) [bounds]
- "only the coins we have can be used" -> p_a[i] <= x_i -> rel(*this, p_a[i], IRT_LQ, x_i) per i and amount
- "minimum number of coins" -> total = sum x_i -> expr(*this, sum(x)) and minimize(total)
- branching: x first (INT_VAR_SIZE_MIN, INT_VAL_MIN), then all payment vectors p_a (INT_VAR_SIZE_MIN, INT_VAL_MIN) so every variable is fixed.
- no global fits the "pay exactly" relation beyond linear with a per-amount payment vector; the decomposition is the payment vector itself, the known coin-change encoding.
