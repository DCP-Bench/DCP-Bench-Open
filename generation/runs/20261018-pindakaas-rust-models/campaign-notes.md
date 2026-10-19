# pindakaas_rust campaign notes

Satisfaction problems only. Pindakaas 0.6.0 has no optimiser, no enumeration and no global
constraints, so the integration (`solvers/pindakaas_rust`, metadata `optimization: false`)
drives CaDiCaL, enumerates with blocking clauses and offers tested decompositions as helpers.
111 of the 112 satisfaction problems are retained, each accepted with at least 80 percent of the
available instances checked (profile: up to 99 instances, 2 solutions, 180 s per instance,
`tolerate_inconclusive`). Written by Haiku agents blind (brief, instance JSON, contracts and the
solver skill only). About 105 were retained on the first attempt.

## Scope

- 119 problems were queued from the reference scan. Seven of them declare an objective in the brief
  and were dropped (blockers recorded): cmo_2012, coin3_application, covering_opl, diet,
  fancy_dress, flip_rows_cols, knapsack. best_host matched the text filter but is a
  satisfaction problem and is retained. That leaves 112 satisfaction problems.
- Not retained: hanging_weights (the diagram does not determine the bar tree; recorded in
  `generation/blockers.json`, retry only after a specification fix). 111 of 112 are retained.

## Changes made during the campaign

The integration was changed once, after the first pass (109 retained), from what the agents
reported. Models retained before that carry the earlier skill and contract digests; ten of them
were re-checked on the rebuilt image and are accepted.

- Wide integers: a linear constraint over an `IntVar` lists every domain value, so domains of
  10^7 need about 1.9 GB and 10^8 abort. Added `Wide`, `wide_int` and `post_wide` (adder
  network over bit literals), bit-backed outputs (`put_bits`, `put` of a `Wide`), automatic bit
  reading for an unencoded `IntVar` output of more than 1024 values, `&Lit` in `put`, and
  `RangeList` and `AdderEncoder` in the prelude. divisible_by_1_through_9 and fibonacci_even
  were retained on retry with the Opus analyst's tested models as hints.
- Contract and skill: measured domain limits, sparse `RangeList` domains, `IntVar::clone` is the
  same variable, double borrow of `s` in one expression, `lit_of` returns `Res<Lit>`, `times`
  memory, std types need a path. New skill example `wide-integers`. Two new readiness checks
  (`wide_output`, `lit_by_reference`). A second standalone review of the updated skill is clean.

## Retained on part of the instances (all at or above 0.8)

| problem | checked | skipped (timeout) |
|---|---|---|
| csplib_007_all_interval | 4 of 5 | json:4 (n=20) |
| csplib_009_perfect_square_placement | 5 of 6 | json:6 (base 112, 21 squares) |
| knights_tour | 4 of 5 | json:2 (10x10) |
| handshaking | 4 of 5 | the example (8 couples), same data as json:0 |

## Near the 180 s limit or slow

csplib_041_n_fractions about 86 s, csplib_003_quasigroup_existence m=9 about 72 s,
csplib_010_social_golfers json:5 about 49 s and json:4 about 27 s, csplib_012_nonogram about 12 s.

## Models to look at (readings the description does not state)

- Assumptions: birthday_coins (at least one coin of each kind, otherwise 3 solutions),
  arch_friends (a clue read as vacuous when the pumps are last), appointment_scheduling (at most
  one person per slot, from a note), crew ("two flights off" read as no work on f+1 and f+2),
  bowls_and_oranges (1-based), crossword ("select 8 distinct words"), clock_triplets (cyclic),
  csplib_049_number_partitioning (A and B ascending), csplib_050_diamond_free (degree modulo 3),
  csplib_011_acc_basketball_schedule (bye convention and readings), csplib_014_solitaire_battleships
  (value 1 forbidden for cells), futoshiki (`lt` rows as [r1, c1, r2, c2], 1-based, first below
  second), kenken (cage operation not in the data, any allowed operation), flow_free_game (induced
  path reading), who_killed_agatha (nobody is richer than himself), session5_climbing_stairs (zeros
  form a suffix), session5_hardy_1729_square (all four numbers different), session5_grocery (product
  is total_price times 100^(n-1)), frog_circle (card 1 at the first position, matched to the
  dataset notes' counts), jobs_puzzle (clue 5 read as three different people; first attempt read it
  as one person doing both and was rejected, retried with that hint from another solver's model).
- Extra work: circling_squares enumerates a 33,752-row table in Rust (squared sums exceeded
  memory as integer variables); crossfigures keeps a local `times_cases` helper over table-allowed
  values; handshaking carries redundant counting constraints; cur_num, curious_set_of_integers
  and dudeney_numbers use sparse `RangeList` domains built from the data.
- 52 problems have a single instance (the example only), accepted on that one instance.
- Fields the brief marks unbindable (kakuro, kenken, csplib_057_killer_sudoku, others) are read
  through `inst.get` and work.
- cur_num's agent read the coordinator's Pindakaas spike report to find the `RangeList` path (not
  a reference or another model).

## Process

Up to 20 agents ran at once, one problem each. A session rate limit stopped two agents once; both
were resumed with SendMessage. Two agents wrote a model file before calling `attempt`; they moved
or removed the unregistered directory (attempt-002 of curious_set_of_integers and of
csplib_041_n_fractions). Opus analyst: the wide-output design and its tested models.
