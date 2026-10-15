Select shifts so that each piece of work is covered exactly once, minimising the number of shifts.
- "a large set of possible shifts, where each shift covers a subset of the tasks" -> x[s] in {0,1} per shift: BoolVarArray(*this, num_shifts, 0, 1) (variable, no constraint)
- "covers each piece of work exactly once" -> per work item w: linear(*this, covering[w], IRT_EQ, 1), covering[w] = the x[s] of shifts containing w (sum of Booleans equals k, linear row)
- "minimizing the total number of shifts used", "cost of each shift is equal" -> total = expr(*this, sum(x)); minimize(total)
- branching -> branch(*this, x, BOOL_VAR_AFC_MAX(0.99), BOOL_VAL_MAX()) with restarts(100): choose shifts first so exact-cover propagation removes overlapping shifts; AFC with Luby restarts for the heavy tail
- output "x" -> the Boolean array x
