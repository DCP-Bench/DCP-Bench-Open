# Models that do extra work outside the solver (mip_cbc campaign)

These retained models were accepted by the evaluator, but part of the reasoning happens in
Python before or around the MIP, or a hint-derived implied constraint carries part of the
search. The CBC image is slow per node, so the retry wave allowed Python-side
preprocessing that is deterministic and derived from the instance data. Sample-based
bounds (random sampling) were rejected: the first RCPSP model used one and was dropped.

| Problem | What the model does outside or beside the solver |
|---|---|
| csplib_012_nonogram | Runs a line-solving propagation over all rows and columns in Python (forward and backward reachability of each block) and fixes the cells it forces; start binaries exist only for the windows that survive. 12 of 13 instances. |
| csplib_011_acc_basketball_schedule | Enumerates the 3^9 venue strings over the nine base dates (Nemhauser-Trick mirror scheme) in Python, keeps those that pass the single-team rules, and gives CBC a one-hot choice per team. |
| resource_constrained_project_scheduling | Computes the horizon with a deterministic serial-schedule heuristic plus a local search in a fixed order, and builds the conflict graph with its maximal cliques (Bron-Kerbosch) in Python. No randomness, no MIP start. |
| broken_weights | Encodes a closed-form criterion (each used weight v satisfies v <= 2 * the total of lighter pieces + 1) instead of the weighing equations. |
| handshaking | Adds an implied row: the two hand counts of each invited couple sum to persons - 2. |
| csplib_003_quasigroup_existence | Uses a pair-image binary shared by four equivalent index tuples, with implied rows that the pair map is a bijection and the diagonal is a permutation. |
| csplib_013_progressive_party_problem | Computes a lower bound on the number of host boats in Python (a closed form of the data). |

Models close to the 180 s limit are kept as they are: acc_basketball (about 120 s),
csplib_023_magic_hexagon (about 108 s), divisible_by_1_through_9 (100 to 112 s),
general_store (about 140 s), quasigroup m=9 (about 102 s), steiner n=19 (about 92 s),
graceful_graphs (about 200 s for the full run), cmo_2012 example (about 137 s).

Also from this campaign: the evaluator accepts a model when at least 80 percent of the
available instances were checked, so several models rest on a timed-out instance
(n_puzzle, cmo_2012, magic_square, knights_tour and tsp, each at exactly 4 of 5 instances;
nonogram is at 12 of 13).
