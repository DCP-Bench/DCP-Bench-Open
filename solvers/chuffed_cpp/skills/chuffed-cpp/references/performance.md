# Chuffed: search and performance lessons

Lessons from writing several hundred Chuffed models for varied combinatorial problems.
The timings were measured on single instances with one thread; treat them as
orders of magnitude, not guarantees. Option names are fields of the global `so`
([core/options.h](https://github.com/chuffed/chuffed/blob/0.14.0/chuffed/core/options.h)),
set before `engine.solve`.

## Branching

- **Always declare `branch(...)` on the decision variables.** Without any `branch` call
  Chuffed reports an unfixed root "solution"; variables that no `branch` reaches and that
  propagation does not fix stay unfixed in the reported solution (a BoolView reads 0).
- Branch first on the structural decisions everything else follows from, then on the
  rest (several `branch` calls are searched in order). Try `VAR_ACTIVITY` or
  `VAR_SIZE_MIN` when `VAR_INORDER` stalls.
- Booleans as decisions: `VAR_SIZE_MIN` on home/away Booleans (as 0..1 `IntVar`s through
  `bool2int`) solved a sports schedule that `VAR_INORDER` stalled on.
- Optimisation that finds one poor solution then stalls: branch on the objective first
  (`VAL_MIN` for minimise, `VAL_MAX` for maximise), then on the decisions. This can fail
  to find any first solution when the cost range is wide; then branch on the decision or
  cost variables with `VAR_MIN_MIN`.
- No custom value order exists (`VAL_RANDOM` aborts at run time). To try values in a chosen
  order, branch on a rank variable `k` and map it with `array_int_element(k, order, x)`.
- A good `branch` usually helps more than redundant implied constraints.

## Restarts and phase

- Library defaults have **no restarts** (`restart_scale` is effectively infinite). For hard
  satisfaction or heavy-tailed search set
  `so.restart_type = LUBY; so.restart_scale = 1000; so.toggle_vsids = true; so.sat_polarity = 2;`
  (`sat_polarity = 2` is anti-polarity; `so.branch_random` exists for randomised restarts).
- Measured on one car-sequencing instance set: restart scales of 100 to 600 left single
  instances unsolved; 1000 with anti-polarity solved all.

## Domains and bounds

- Tighten domains from the data (a shipment is at most min(capacity, demand)). Every
  auxiliary `IntVar` needs a domain that holds all its values, and no wider.
- Add implied constraints that bound the objective: cost >= demand x cheapest unit cost,
  via `minimum`, cut one facility-location optimality proof from 190 s to 36 s.
- Weak optimisation bounds: compute stronger bounds in the program from the data
  (Lagrangian or reduced-cost preprocessing, then add the penalties to the costs).
- Count indicator literals directly in the objective instead of summing derived
  Booleans; the summed form left the solver searching for the bound.
- Optimality proof too slow on a grid of costs: add per-row and per-group cost variables
  with lower and upper bounds from the data (the sum of the c smallest and of the c
  largest costs).
- A redundant sum constraint (the answers sum to n(2n+1)) fixed a time-out on a handshake
  puzzle: implied sums can help where a branch alone does not.

## Symmetry

- Symmetric multisets (the faces of a die, the members of a group): search a sorted copy
  and link the reported values through a permutation (`all_different` on positions plus
  element constraints), so every order of the reported values stays reachable.
- Add symmetry breaking (`lex`, a fixed first value) only when every solution you need is
  still reachable; `lex` crashed (signal 11) on rows of eager 0/1 variables.
