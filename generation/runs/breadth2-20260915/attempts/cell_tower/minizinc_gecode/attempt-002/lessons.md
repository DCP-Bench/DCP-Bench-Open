Attempt 001 was rejected as `invalid_solution`, and the cause is in MiniZinc's
flattening, not in the constraints as written.

The reference bounds each region's coverage from one side only:
`covered[j] <= sum_i delta[i][j] * build_tower[i]`. Translating that literally
and adding the budget constraint, MiniZinc 2.9.3 produced a FlatZinc in which
`build_tower[2]` appears in **no constraint at all**, the budget constraint
having been flattened as `3*build_tower[1] + 4*covered[2] <= 4`. The freed
variable then takes either value, so the runner emitted `build_tower = [true,
true]`, which spends 7 against a budget of 4. MiniZinc's own output item
evaluates the budget constraint to `false` on that solution, and Chuffed
reproduces it, so it is the flattening rather than Gecode.

Attempt 002 states coverage as an equivalence — a region counts as covered
exactly when one of its sites is built — which flattens soundly. It does not
narrow what the declared outputs may be: the runner pins the proven optimum and
enumerates, and at the optimum the reference's `covered` is maximal for the
chosen towers anyway, so the (build_tower, objective) pairs are the same.
