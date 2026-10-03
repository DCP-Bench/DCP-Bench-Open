# Lesson: a docplex sum used again in arithmetic can change in place

Attempts 001 and 003 declared each seat as `model.sum(s * at[i, s] for s in range(3))`
(the s = 0 term has coefficient 0) and then used that expression in further arithmetic
(`a == b + 1 - 3 * wrap` in 001, `a - b + 3 * wrap == 1` in 003). Both were rejected with
`invalid_solution` although the constraints are those of the reference. Attempt 002 declares
each seat as an `integer_var` linked by `seat == model.sum(...)` and uses only the variables
afterwards; it was accepted.

DOcplex's `LinearExpr.plus` / `minus` call `clone_if_necessary`, which returns the expression
itself, not a copy, when it is transient and not yet in a constraint. The likely cause is that
the declared output expression was modified in place by `a - b` / `b + 1`, so the runner read a
different expression than the seat. Not verified inside the image: clock_triplets (sums over
values 1..12, no zero coefficient) reused `x[i] + x[i-1] + x[i-2]` and was accepted.

Safe pattern: when a declared output expression is reused in arithmetic, declare it as an
integer variable linked by one equality, or never put it as the left operand of `+`/`-`.
