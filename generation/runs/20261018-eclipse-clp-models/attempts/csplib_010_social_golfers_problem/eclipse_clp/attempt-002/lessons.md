# Lessons: csplib_010_social_golfers_problem (eclipse_clp)

- Attempt 001 (ic, default input-order labeling): accepted on 5 of 8 instances; json:4, json:5, json:6 hit the 180 s budget. 5/8 = 0.625, below the 0.8 retain gate, so not retained.
- Attempt 002 (same model, `search_goal/1` with `first_fail`/`indomain_min`): accepted on 7 of 8; json:4 (8 weeks, 5 groups, size 2) still timed out. 7/8 = 0.875, retained.
- Reification syntax in ic: `B #= (X #= Y)` works; `B #<=> (X #= Y)` is a syntax error in ic.
- Open gap: json:4 remains a performance limit for this formulation.
