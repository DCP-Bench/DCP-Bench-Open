# csplib_007_all_interval, highs_cpp: lessons

Free checks (`evaluation.check`, 2 instances, solution limit 2, execution timeout 180 s).

- attempt-001 (position permutation x via binaries y, diffs via big-M abs with a sign binary per pair,
  M = 2(n-1)): example (n=12) accepted; json:1 (n=13) timeout at 180 s with only the first solution found.
- attempt-002 (same permutation, signed-difference binaries per pair and size, no big-M): example
  accepted in 59 s; json:1 (n=13) timeout again with one solution.
- attempt-003 (attempt-002 plus adjacency binaries adj[i][a][b] linearising y[i][a] y[i+1][b], with
  pair-once and degree rows): the example itself timed out. The extra rows slowed the search.

Reading: the first solution comes in roughly 40 to 60 s at n=12, and the second solve (after the
no-good over x and diffs) does not finish within 180 s at n=13. The timeout is the solver's search on
the second solution, not a wrong model: every reported solution was checked and accepted.
Instance hits: the example passes in attempts 1 and 2 only, so instances_checked / instances_available
is 1/5, below the 0.8 retention threshold. Not retained.

Not tried: a formulation the reference's CP search would handle differently, such as a Hamiltonian
path over pitch-class edges with subtour cuts. A MIP with subtour elimination needs lazy cuts that the
integration does not provide.
