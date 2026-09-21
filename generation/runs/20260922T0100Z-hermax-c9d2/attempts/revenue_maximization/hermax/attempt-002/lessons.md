# revenue_maximization — a performance limit, not a repair

attempt-001 was killed by the memory limit (`exited -9`). The objective variable
is one-hot encoded, so its domain is its cost, and a plain
`0..sum(revenue * demand)` range is 9001 values. Tying that to the expression
builds two pseudo-Boolean constraints per value, which exhausts 2 GiB.

attempt-002 narrows the domain to totals the revenues can actually reach. With
revenues 100 and 150 those are the multiples of 50 up to 9000, so 181 values
rather than 9001, and the memory problem goes away.

It then times out instead, at the run's full 180 seconds. That is honest: the
model is right, and EvalMaxSAT simply cannot prove this optimum inside the
budget. A MaxSAT objective is a set of soft clauses, so an objective ranging
over 181 values means 181 soft units the solver has to reason about, and proving
optimality across them is the expensive part.

Left unretained and not added to `generation/blockers.json`: a sharper encoding
of the objective, or a different MaxSAT backend, may well succeed, so the pair
should stay in the queue rather than be written off.
