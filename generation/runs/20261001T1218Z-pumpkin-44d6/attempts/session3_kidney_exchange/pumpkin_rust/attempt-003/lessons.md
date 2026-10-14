# Lesson (pumpkin_rust)

With an objective, the runner proves optimality through LinearSatUnsat. An objective
variable whose domain is far looser than any reachable value (here 0..n*n for a count
that can never exceed n) left the optimum unproven on a 20-person instance (attempt-001
and attempt-002, execution_timeout). Building the objective as a sum of per-receiver
0/1 variables, which bounds it by n, solved the same instance in 2.7 s (attempt-003).
Evidence: attempt-002/evaluation.json vs attempt-003/evaluation.json, instance json:4.

Related: for Hamiltonian-path problems (knights_tour, calvin_puzzle), half-reified arc
literals with `x[t] = x[s] + 1` and degree constraints solved 10x10 in 22 s, where an
inverse-position model with `table` + `element` channelling timed out on 8x8
(knights_tour attempt-001 vs attempt-002).
