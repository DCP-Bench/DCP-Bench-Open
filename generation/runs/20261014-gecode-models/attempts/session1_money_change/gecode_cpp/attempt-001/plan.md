Alice has to give Bob some change; she has coins of several types, each type with a limited number available. Counts are integers from 0 up to the number of coins available of that type.
-> coin_counts = IntVarArray(*this, n, 0, max(available)); then rel(*this, coin_counts[i] <= available[i]) per type (bounds from the instance field available_coins)
The change must add up to the amount: the sum of count times coin value equals the amount.
-> linear(*this, IntArgs(types_of_coins), coin_counts, IRT_EQ, amount, IPL_BND) (weighted sum, bounds consistency)
Minimise the number of coins used: total = sum of all counts.
-> total = expr(*this, sum(coin_counts)); minimize(total) (branch and bound, default BAB)
Branching on the counts, smallest domain first, trying the largest count first so good solutions appear early.
-> branch(*this, coin_counts, INT_VAR_SIZE_MIN(), INT_VAL_MAX())
Output: the number of coins of each type, in the order of the types.
-> output("coin_counts", coin_counts)
