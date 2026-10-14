# Lessons (picat)

- csplib_013 (min hosts), coins_grid (min cost) and csplib_009 (perfect squares): the cp
  encoding timed out on the larger instances (attempt-001 evaluations), the same
  constraints under `import sat.` solved every instance in under 70 s. When a cp attempt
  times out on an optimisation or exact-packing problem, try sat before adding search code.
- coins_grid under sat: redundant per-row and per-column cost variables with a lower bound
  (the sum of the c smallest distances in the line) cut the largest instance from 107 s to
  17 s (direct evaluation.check runs).
- car sequencing under cp: renumbering the types by difficulty and labelling slots left to
  right, plus prefix/suffix cumulative-count bounds as variable domains, solved all 22
  instances; the same constraints written as long window sums overflowed Picat's trail.
