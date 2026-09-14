Attempt 001 was accepted but Gecode hit the 180 s execution timeout on k = 16,
19 and 20. Attempt 002 keeps the same solution set and adds two implied
constraints for propagation:

- each value occupies exactly two places of `sol` (global cardinality), which
  attempt 001 only implied through the element constraints;
- the first place of value i cannot be later than 2k - i - 1, which follows from
  `position[i + k] = position[i] + i + 1`.
