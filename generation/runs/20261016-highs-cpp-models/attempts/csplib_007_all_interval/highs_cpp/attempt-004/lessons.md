# csplib_007_all_interval, highs_cpp: lessons

attempt-004 is attempt-002 plus two implied rows: sum of diffs = n(n-1)/2 and sum of x = n(n-1)/2.
Symmetry breaking was not used: solvers/CONTRACT.md forbids symmetry breaking the description does not ask for.

Evaluation: accepted, instances_checked 4 of 5 (example n=12, json:1 n=13, json:2 n=14, json:3 n=5 accepted).
json:4 (n=20) times out at 180 s with no solution. 4/5 = 0.8, so retained.

Earlier attempts 001 to 003 failed on the second solution at n=13 or on the example itself (attempt-003, extra adjacency rows).
Not tried: an edge-based Hamiltonian path formulation with MTZ order variables (weak LP, untested).
