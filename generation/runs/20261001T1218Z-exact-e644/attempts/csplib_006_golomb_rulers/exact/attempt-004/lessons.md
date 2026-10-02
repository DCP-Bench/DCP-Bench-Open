Optimisation proofs in Exact depend on linear lower bounds that follow from the problem and that the
solver does not derive from indicator encodings. Golomb rulers, evaluation.json of each attempt:
- attempt-001 (difference indicators per pair of marks): sizes 5 and 7 solved; 8, 9, 10 timed out.
- attempt-002 (position indicators, at most one pair per distance): size 8 in 79 s; 9 and 10 timed out.
- attempt-003 (adds pairwise span bounds): size 8 in 63 s; 9 and 10 timed out.
- attempt-004 (adds, for each g, "the differences between marks at most g places apart are distinct
  positive integers, so their sum is at least 1 + ... + their count"): sizes 8, 9, 10 in 16 s,
  143 s and 123 s, all five instances accepted.
