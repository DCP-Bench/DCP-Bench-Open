# Lesson: Golomb rulers in z3_python

Measured on this run's evaluator records (execution timeout 180 s, 5 instances, 5 to 10 marks):

- Integer marks with `Distinct` over differences (earlier run z3-20260910t125536z-166594-r3,
  attempt-001): 0 of 3 instances.
- Boolean position encoding with a sum-of-`If` objective (attempt-001): 5, 7 and 8 marks
  accepted (8 marks in 29.8 s); 9 and 10 timed out.
- Order-encoded marks with sub-ruler span bounds as binary clauses (attempt-002): 8 marks in 7.1 s;
  9 and 10 still timed out. `If`-chain outputs (attempt-004) made no measurable difference.
- Replacing "pair Booleans + `AtMost(pairs_d, 1)`" with direct 4-literal clauses
  `not(on[p] and on[p+d] and on[q] and on[q+d])` (attempt-005): all 5 accepted, 9 marks in 18.2 s,
  10 marks in 123.7 s. The same logic re-run (attempt-006, comments only) timed out on 10 marks at
  181.9 s, so 10 marks is near the limit.
- Dropping the window `AtMost` constraints (attempt-008) or also replacing `PbEq` by clauses
  (attempt-007) was slower: 9 marks in 68.8 s and 63.4 s.
