# huub_rust campaign notes

164 of 164 problems retained, each accepted with at least 80 percent of the available instances
checked (profile: up to 99 instances, 2 solutions, 180 s per instance, `tolerate_inconclusive`).
Written by Haiku agents blind (brief, instance JSON, contracts and the solver skill only).
About 150 were retained on the first or second attempt. Five were retried after Opus analysts
wrote tested hints: `tsp`, `csplib_002_template_design`, `handshaking`, `fibonacci_even` and
`csplib_008_vessel_loading`. A sixth analyst tested `no_overlap` (see below).

## Changes made during the campaign

The skill and the contract were corrected once, after about 120 retained models, from what the
agents reported. Models retained before that carry the earlier skill digest.

- `IntLinearExp::from` accepts only `i64` and `View<i64>`; a `View<bool>` does not convert (the
  skill said it did, and about 25 agents hit the compile error). Working forms are now listed.
- `reified_by` is an equivalence and `implied_by` the one-way form; using the first for a one-way
  switch makes the model infeasible with no error (hit in age_changing, water_bucket,
  fibonacci_even and others).
- A 2-term equality can hang in `post()` also over distinct pairs (contracting_costs), not only
  two over the same pair. `eq2` is the safe form.
- `no_overlap` nests per object, not per dimension (`vec![xs, ys]` compiles and constrains almost
  nothing). With sizes that are decision variables Huub 100.1.0 can return overlapping solutions
  (rare, found on random 4-object instances), and `strict(false)` drops solutions with zero-size
  objects. Fixed sizes in strict mode matched brute force on 29 random instances (csplib_009 is
  safe). With variable sizes, post the pairwise disjunction.
- A fresh standalone review of the updated skill is clean.

## Retained on part of the instances (all at or above 0.8)

| problem | checked | skipped (timeout) |
|---|---|---|
| csplib_001_car_sequencing | 19 of 22 | json:3, json:4, json:10 (full evaluation about 22 min wall) |
| coins_grid | 4 of 5 | json:4 (12x12) |
| facility_location | 4 of 5 | json:4 |
| tsp | 4 of 5 | json:2 (berlin52_first20) |

## Near the 180 s limit or slow

csplib_032_max_density_still_life 8x8 (about 90 s), cmo_2012 example (about 90 s), tsp json:3
(about 75 s), csplib_010_social_golfers (about 41 s), flowshop_scheduling (about 35 s),
csplib_002_template_design json:2 (about 33 s), csplib_006_golomb_rulers and others at 20 to 30 s.
On a slower machine these may time out.

## Models to look at (extra work, assumptions or readings the description does not state)

- curious_set_of_integers: the only solution accepted is `number = 0` (0*a + 1 is a square for
  every a); the description's wording allows it, the intended answer may differ.
- Bounds chosen by the agent, not given: csplib_006_golomb_rulers (marks in 0..n*n), cmo_2012
  (`max_val` for a, b, n, p; primes sieved in Rust; implied bounds b < n < a), archery_puzzle
  (per-hit bound), bus_scheduling (x[i] up to the largest demand), session1_guards_and_apples
  (domain up to 2^(gates+2)), diet, csplib_076_costas_arrays (difference domain, no comment),
  twelve_pack (total from a greedy argument), coins_grid.
- Extra work from the retry round: tsp (successor/predecessor model, MTZ ranks, two cheapest
  arcs per city, 2- and 3-cycle cuts), csplib_002_template_design (implied bound
  sheets * slots >= total demand, slots filled), handshaking (redundant couple sums),
  fibonacci_even (term count and result bound computed in Rust from the limit), knights_tour
  (successor model with a dummy node).
- csplib_039_rehearsal leaves gaps out (argued not to change the optimum); fancy_dress leaves the
  "$9 otherwise" term out (does not change the optimum); frog_circle fixes card 1 at the first
  place because the reference counts arrangements up to rotation; session2_movie_scheduling
  counts touching endpoints as overlap; session5_grocery scales the product by 100^(n-1)
  (the description does not say dollars).
- Block comments in the agent's own words, not the description's: calvin_puzzle (element
  channelling), circling_squares (squares).
- The brief or description is ambiguous in: jobs_puzzle (clue 5), crossword, session3_exodus,
  football, best_host, kakuro (`blanks` marks black cells, undocumented), csplib_008_vessel_loading
  (reference wants bottom < top with top = bottom + extent, and rotation allowed).
- Dataset notes that state answers or reference bounds (not used by the models): handshaking
  ("answer 4"), mario (strict fuel bound), session1_guards_and_apples (0..100 bound), diet,
  prod, fixed_charge, football (reference optimum in the note).
- Problems with a single instance (the example only) were accepted on that one instance: 52 of
  the 164; read those models yourself before relying on them.
- Fields the brief marks unbindable (cabling, session2_movie_scheduling, session3_kidney_exchange,
  csplib_057_killer_sudoku, csplib_022_bus_driver_scheduling, kakuro, jobshop) are read through
  `inst.get` / `inst.cube` and work; `next_work` does not withhold them.
- session1_thick_as_thieves: an earlier formulation with `.reify()` on an output-connected view
  crashed the runner with SIGSEGV after the first solution; the retained model avoids it. The
  crash was not reproduced separately.

## Process

Up to 20 agents ran at once, one problem each. A session rate limit (HTTP 429) stopped 15 agents
for a while; they were resumed with SendMessage. Two agents misread a one-word problem name as an
incomplete message; both were resent with explicit wording. Opus analysts: no_overlap behaviour
(and the vessel_loading convention), tsp and template_design hints, handshaking and
fibonacci_even hints.
