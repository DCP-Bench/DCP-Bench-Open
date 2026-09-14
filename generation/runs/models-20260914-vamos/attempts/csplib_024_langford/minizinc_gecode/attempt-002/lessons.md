Attempt 001 was accepted but Gecode hit the 180 s execution timeout on k = 16,
19 and 20. Attempt 002 keeps the same solution set and adds two implied
constraints for propagation:

- each value occupies exactly two places of `sol` (global cardinality), which
  attempt 001 only implied through the element constraints;
- the first place of value i cannot be later than 2k - i - 1, which follows from
  `position[i + k] = position[i] + i + 1`.

Result: the implied constraints moved Gecode from 2 of 5 instances to 3 of 5
(k = 12, 15, 16 now finish; k = 19 and k = 20 still hit the 180 s execution
budget). Retained with that coverage, as a Gecode performance limit rather than
a modelling error: CP-SAT and CPMpy solve all five with the same formulation.
