# csplib_008_vessel_loading, maxicp_java: retry lessons

Result: accepted, but only 3 of 5 instances checked (example, json:3, json:4). json:1 and json:2
hit the 180 s execution timeout with no solution, so the pair is 60% checked and not retained
(the rule is at least 80%). Reported as a performance limit.

What changed from attempt-001:
- The separation relations are reified into booleans that are unregistered (`makeBoolVarArray`
  on the CPFactory side) and fixed by propagation once the positions are fixed. The search now
  branches only on `turned` and the positions. Timeouts on json:1 remain.
- The "relation holds" value is the left branch of firstFailBinary (`neg = 0`), and the disjunction
  is `sum(neg) <= 3`.

What did not help: branching on the separation booleans (attempt-001 and the first attempt-002
variant) also timed out on json:1.

Observations for the next try:
- json:1 has containers with total area 256 on a 16x16 deck, so it is a perfect packing. Any gap
  between a class-2 and a class-3 container (separation 2) needs the strip beside it to be covered
  by other containers, which DFS with bounds propagation does not see early.
- The example and json:3 and json:4 solve in under 3 s, so the encoding is correct on those.
- A stronger encoding for the perfect-packing case (redundant area bound, stronger non-overlap
  reasoning per axis) is the next thing to try. Not tried here.
