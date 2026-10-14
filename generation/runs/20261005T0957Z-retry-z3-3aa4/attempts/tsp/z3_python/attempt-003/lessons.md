# Lesson: TSP in z3_python

Measured on evaluator records (execution timeout 180 s, 5 instances, 6 to 30 cities):

- Arc Booleans, integer MTZ positions, integer length variable (run 20260929T1400Z-z3-mzn-swipl-7a2e,
  attempt-001): only the 6-city instance.
- Purely Boolean model (order-encoded MTZ positions, `PbEq` degrees), objective written as
  assignment-dual lower bound + `Sum(If(arc, reduced_cost, 0))`, reduced-cost arc fixing against a
  2-opt upper bound, one-orientation symmetry breaking (attempt-001): 4 of 5, berlin52_first20 timed out.
- Adding Held-Karp 1-tree arc exclusion (subgradient, marginal cost test against the 2-opt bound)
  (attempt-002/003): all 5 accepted, each in under 5 s.
- The output is declared as the same expression as the objective, so that (inferred, not
  measured separately) the runner's blocking clause contradicts `objective == best` directly.
