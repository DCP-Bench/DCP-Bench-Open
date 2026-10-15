Cut rolls of width RollWidth into pieces of the given widths; each pattern gives how many pieces of each width one roll yields.
Choose how many rolls to cut with each pattern.
- each pattern is used a whole number of times, from 0 to a bound from the data -> IntVarArray x(num_patterns, 0, ub_p) with ub_p = max over used widths of ceil(orders[w] / pieces[p][w]) -> domain bounds from the instance
- for each width, the pieces cut from all rolls meet its orders: sum_p pieces[p][w] * x_p >= orders[w] -> linear(*this, IntArgs(pieces[.][w]), x, IRT_GQ, orders[w]) (weighted sum, no globals fit)
- minimise the total number of raw rolls cut -> total = expr(*this, sum(x)); minimize(total)
- branching: pattern counts first, value split from the top (INT_VAL_MAX) to reach a good first solution; no auxiliary variables remain
