# jobshop on eclipse_clp, attempt 001: lessons

Evaluation: accepted=true, but instances_checked 2 of 5 (ratio 0.4 < 0.8). Not retained.
Timeouts: json:1 (ft06, 6x6), json:2 (la01, 10x5), json:4 (gen_6x3). Checked: example, json:3.

What the timeouts show:
- The optimum phase is fast. ft06 reaches its optimum 55 in about 0.03 s with
  `ic_edge_finder` `disjunctive/2`, `smallest`/`indomain_min`, under the driver's own bb_min options.
- The timeout is in the enumeration phase after the proof. The outputs are only `makespan`, so every
  later solution is a duplicate, and the driver must exhaust the search with `Makespan = optimum`.
  Exhausting took more than 55 s on ft06 in an ad hoc run (`ic_edge_finder` and `ic_edge_finder3`,
  `smallest` and `first_fail`). Under `gfd` the optimum phase itself did not finish within 170 s.
- The number of complete start vectors at the optimum is set by the problem, not by propagation, so a
  complete labelling of the start variables cannot be made fast by a stronger formulation alone.

Formulations tried inside this attempt (all with the same enumeration problem):
- Makespan as `max` over per-job end variables (`Makespan #= max(Ends)`).
- Makespan as an upper bound on every task end (`S + D #=< Makespan`). Current model.

Not tried: an incomplete search_goal that commits to one start vector per machine ordering. That
would be fast, but search_goal/1 must be a complete search (solvers/CONTRACT.md, eclipse_clp
CONTRACT.md "Solving"), so it was not used. This needs a decision by the contract owner.
