# facility_location, maxicp_java: lessons from the retry

Result: not retained. Attempt 3 is accepted on 3 of 5 instances (example, json:1, json:3, 60%). json:2 (4 regions) and json:4 (5 regions) hit `execution_timeout` with "Candidate optimum was not proven". The retain rule needs at least 80% of available instances checked.

What failed, in order:
- Attempt 1 (original model): json:2 and json:4 timed out. Shipping cost bounds were weak, so the optimum was not proven within 180 s.
- Attempt 2 (adds channelling `ships <= open * min(cap, demand)`, implied capacity and coverage constraints, and a per-region table with the cheapest open warehouse cost): json:2 and json:4 still timed out. The example solve time went from 57 s to 97 s, so the extra constraints did not pay off.
- Attempt 3 (table gives the greedy cost of covering each region's demand from the open set, under the per-warehouse cap): example 78 s, json:1 40 s, json:3 2 s, json:2 and json:4 still timed out.

Diagnosis: time goes to the optimisation phase, not to enumeration (json:1 with solution limit 1 takes as long as with 2). The driver branches with `firstFailBinary`, which tries `x = min` then `x != min`. On a ship variable with domain 0..100 this scans values one at a time, and the ship variables carry most of the search. Bounds from the open pattern are now strong, but the capacity shared between regions is not captured by any linear or table bound the model can post cheaply, so each open pattern is still searched value by value.

Next steps, not tried: a binary or otherwise coarse encoding of the ship amounts so that the search has fewer value steps per variable; or a runner-side change to value ordering, which belongs to the integration (`solvers/maxicp_java`), not this model.
