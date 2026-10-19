# Lessons: resource_constrained_project_scheduling, eclipse_clp

Attempt 3 (ic, ic_edge_finder cumulative per resource, input_order/indomain_min,
energy lower bound on the makespan) was rejected with no_instance_verified: every
instance hit execution_timeout during the optimum phase (proof of optimality not
reached in 180 s). Before this, attempt 1 (ic, smallest/indomain_min) was accepted on
the example instance (optimum 21) but timed out on json:1 (optimum 43).

Probes with the container (not evaluated, 60 s bb_min on json:1, cost reached):
- smallest/indomain_min, cumulative (edge finder): 61
- first_fail/indomain_min: 53
- first_fail/indomain_split: 53
- input_order/indomain_min: 49 (also with energy bound: 49)
- ic_edge_finder3 cumulative with smallest: 61
- gfd cumulative with input_order: 49, gfd with smallest timed out on the example

No variant reached the optimum 43 for json:1 within the budget. The gap points to
the search and the propagation for proof, not to the constraint encoding. Possible
next steps not tried: stronger propagation or a better search order for the proof.
