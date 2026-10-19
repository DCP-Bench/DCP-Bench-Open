# tsp on huub_rust: lessons from attempts 001 to 003

Result: each attempt is accepted on the instances it finishes, but none reaches the 0.8
coverage needed to retain. Instances 1 to 3 of 5 (eil51_first20 at 20 cities, berlin52_first20
at 20 cities, eil76_first30 at 30 cities) hit the 180 s execution timeout with "the optimum
was not proven".

| attempt | formulation | instances_checked / available | notes |
|---|---|---|---|
| 001 | `circuit` on successors, one `element` per leg, objective = sum of legs | 3 / 5 | example 0.2 s, 12 cities; berlin52_first20 and eil76_first30 time out |
| 002 | attempt 1 plus per-leg domains (row min..max) and total bounds, and reified "exactly one leg per city" Booleans | 3 / 5 | same two timeouts; no faster |
| 003 | `circuit`, reified leg Booleans, objective = sum of `uses[i][j] * d[i][j]` (no element) | 2 / 5 | example takes 31 s; eil51_first20 now also times out |

Findings:
- The distance objective through per-leg `element` (001, 002) is the best of the three.
- A weighted sum of reified Booleans (003) propagates worse and is much slower.
- `IntLinearExp::from(View<bool>)` does not compile; `View<bool> * i64` does, and sums of
  Booleans with `sum::<IntLinearExp>()` work.
- The `circuit` helper (order variables plus n-1 element constraints) is probably the main
  cost on 20 to 30 cities. Not tried: a model with a different successor encoding or a tour
  ordering built from the instance (the description asks for none).
