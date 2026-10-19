# cvc5 (Python) campaign notes

Run `20261017-cvc5-python-models`, solver `cvc5_python` (cvc5 1.4.2 through `cvc5.pythonic`).
Profile: 99 instances, 2 solutions, 180 s, `tolerate_inconclusive`. A model is retained when the
evaluator accepts it with at least 80 percent of the available instances checked.

Two things changed during the run and are worth knowing when reading the attempts.

- The run was created with the default profile (1 instance, 60 s) and corrected to the campaign
  profile after the first agents reported. Attempts made before the fix were re-evaluated as new attempts.
- The runner rebuilt a fresh solver from the assertions of the returned `Solver`, so `SolverFor(...)`
  and options set on it were ignored. It now copies the logic and the user-set options (commit
  `fe13c453c`; `tlimit-per`, `tlimit`, `incremental` and `produce-models` stay with the runner).
  Models retained before that commit ran under the default logic; six of them return `SolverFor`
  and were re-checked after the fix (none slower, `csplib_008_vessel_loading` json:1 went from a timeout to accepted).

## Models that do extra work outside the solver, or add derived constraints

Python-side work is deterministic and derived from the instance or the description. No sampling.

| Problem | What the model does |
|---|---|
| csplib_006_golomb_rulers | greedy first-fit ruler length from the size alone as the upper bound |
| resource_constrained_project_scheduling | longest-path earliest and latest start bounds from the precedence links; `start_time[0] = 0` |
| tsp | the most Python-side work of the campaign, all named in the model header: a Hungarian assignment lower bound whose reduced costs prune arcs, an upper bound from nearest-neighbour tours plus 2-opt in a fixed scan order (`total <= UB`), and a Held-Karp 1-tree bound by subgradient ascent that removes edges which cannot lie on a tour no longer than UB. It does not compute the optimum; the solver still searches and proves it. Without this the 12-city example took 74 to 102 s and the 20-city instances timed out. Worth a second look from you |
| mario | Floyd-Warshall shortest fuel distances forbid arcs and houses that cannot fit the fuel limit |
| dudeney_numbers | `number == root^3` as a disjunction over the candidate roots whose cube has at most n digits |
| ages_of_the_sons | the triples with product 36 are enumerated in Python, the clues constrain the candidates |
| cur_num, curious_set_of_integers, giant_cat_army | square tests as an `Or` over constant squares up to the bound |
| csplib_021_crossfigures, csplib_041_n_fractions | products split into case splits over constants (the 21 two-digit primes; one digit) |
| cmo_2012 | the lookup tables encode that both numbers are squares, derived from the difference being prime |
| session5_grocery | the product is taken on double-width bit-vectors, linked back with `BV2Int` |
| general_store | letters are 8-bit bit-vectors; `SolverFor("ALL")` with `bv-solver=bitblast-internal` |
| csplib_032_max_density_still_life | window caps from still-life theory (3x3 at most 6, 2x3 and 3x2 at most 4) as implied rows, validated by the evaluator matching the three optima |

Derived redundant totals (implied by the statement, not extra search restrictions): csplib_053_graceful_graphs
(label sum), heterosquare and csplib_023_magic_hexagon and session1_magic_square (cell total, line-sum bounds),
csplib_049_number_partitioning (sum and sum of squares), csplib_044_steiner (degree sum),
csplib_019_magic_squares_and_sequences, autoref (two count identities and the 0..n bound),
csplib_011_acc_basketball_schedule (byes and games per team and date), csplib_002_template_design
(per-variation copy bound), csplib_001_car_sequencing (prefix capacity bounds as Boolean counters).

## Coverage below 100 percent (all at least 80 percent)

26 models rest on a timed-out instance: bin_packing, broken_weights, cmo_2012, coins_grid, covering_opl,
csplib_005_autocorrelation, csplib_006_golomb_rulers, csplib_007_all_interval, csplib_008_vessel_loading,
csplib_009_perfect_square_placement (5 of 6), csplib_012_nonogram (12 of 13), csplib_013_progressive_party_problem
(8 of 9), csplib_024_langford, csplib_050_diamond_free (5 of 6), csplib_076_costas_arrays, devils_word,
flowshop_scheduling, frog_circle, heterosquare, jobshop, knights_tour, mario, n_puzzle, session3_farmer_and_cows,
session5_grocery, sudoku (all others 4 of 5).

## Close to the 180 s limit (kept)

csplib_032_max_density_still_life json:2 (about 171 s), csplib_034_warehouse_location json:2 (about 155 s),
csplib_023_magic_hexagon (about 139 s), csplib_010_social_golfers_problem json:4 (about 136 s),
csplib_009_perfect_square_placement json:5 (about 110 s), football (about 97 s), mario json:3 (about 95 s),
csplib_074_maximum_clique json:3 (about 93 s), csplib_057_killer_sudoku (up to 91 s), session1_magic_square
json:4 (about 77 s), crypta (about 72 s), pythagorean_triplet (about 62 s), coins_grid example (about 57 s).

## Process notes

- `jobshop`: the agent printed the first 1.5 KB of `dataset/jobshop/jobshop.cpmpy.py` while listing the
  folder (header, data, imports; no constraints). The model is the textbook pairwise no-overlap. It is
  kept; a blind redo is a one-agent job if you prefer one.
- `autoref`: the instance note for n=3, m=0 says the solution is unique, but (4,0,0,0,0) also satisfies the
  description when the counts are not bounded by n. The evaluator accepts the bounded reading.
- `coin3_application` had two retained copies for a moment (the first without block comments); only attempt-004 is kept.
- The brief lists some fields as unbindable (ragged rows, mixed types, for example `cabling`, `csplib_022_bus_driver_scheduling`,
  `csplib_057_killer_sudoku`, `session2_movie_scheduling`); the cvc5 runner binds them as plain Python values and all of them evaluated.
- A stray probe container (`probe4.py global`) from the setup phase kept running for hours; stopping it was denied, so it is still there.
