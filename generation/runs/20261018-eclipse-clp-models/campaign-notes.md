# eclipse_clp campaign notes

164 of 164 problems retained, each accepted with at least 80 percent of the available
instances checked (profile: up to 99 instances, 2 solutions, 180 s per instance,
`tolerate_inconclusive`). Written by Haiku agents blind (brief, instance JSON, contracts and the
solver skill only). 153 were retained on the first pass. The other 11 were retried after an
analyst (Opus) wrote tested hints, with Sonnet agents for the hardest cases.

## Changes made during the campaign

- The driver ends the enumeration phase at once when the declared outputs are already ground and
  equal to a reported solution. Before, a model whose only output is the optimum (jobshop) walked
  every optimal start vector before reporting `complete`. New readiness check `objective_only_output`.
- The skill corrected `circuit/1` (it demands one cycle through every variable, no self loops) and
  gained the traps agents hit: `param/1` in every `do` loop, nested expressions posted through a
  variable, `mod` and `//` on unbound variables, missing builtins (`between/3`, `append/2`,
  `atom_codes/2`, `string_to_list/2`), `floor/1` returning a float, array access with `=`, nested
  `and`/`or` in reification, prefix-operator output names. The CONTRACT no longer calls singleton
  warnings harmless. A fresh standalone review of the updated skill is clean.

## Retained on part of the instances (all at or above 0.8)

| problem | checked | skipped (timeout) |
|---|---|---|
| csplib_001_car_sequencing | 20 of 22 | json:17, json:20 |
| csplib_009_perfect_square_placement | 5 of 6 | json:6 (base 112) |
| csplib_010_social_golfers_problem | 7 of 8 | json:4 |
| csplib_012_nonogram | 11 of 13 | json:2 (25x25), json:6 (35x60) |
| csplib_013_progressive_party_problem | 8 of 9 | json:8 |
| csplib_034_warehouse_location | 4 of 5 | json:3 |
| coins_grid | 4 of 5 | json:4 (12x12) |
| equal_sized_groups | 4 of 5 | the 1000-element instance |
| facility_location | 4 of 5 | json:4 |
| multi | 4 of 5 | json:4 |
| resource_constrained_project_scheduling | 4 of 5 | json:2 (optimum 53) |
| session3_kidney_exchange | 4 of 5 | json:4 |
| tsp | 4 of 5 | json:2 (20 cities) |

## Near the 180 s limit

csplib_006_golomb_rulers example (about 136 s), csplib_056_sonet example (100 to 115 s),
n_puzzle json:4 (86 s), csplib_026_sports_tournament_scheduling example (92 s), tsp json:3 (78 s),
csplib_032_max_density_still_life 8x8 (72 s), mario json:1 (66 s), session5_grocery (54 s).
On a slower machine these may time out.

## Models to look at (extra work or readings the description does not state)

- csplib_011_acc_basketball_schedule: posts per-date counts (one bye, four home, four away) that the
  description does not strictly imply, and a venue pattern table enumerated in Prolog.
- big_bang2: the search order uses a balance guide with the constant 39 chosen by the analyst.
- autoref: bounds every term to 0..n, read from the instance notes.
- diet: variable domains 0..max(limits), a modelling choice and not a proven bound.
- cmo_2012: uses `max_val` as the bound of a, b and n.
- archery_puzzle: per-hit bound derived in a comment; assumes positive ring scores.
- session5_grocery: the description does not say the product is in dollars; the model took the
  scaling from the instance note.
- hanging_weights: block comments paraphrase the diagram, not the description.
- handshaking: `search_goal/1` commits with `once` to one completion after the output is labelled
  (safe: the only output is fixed by the first labelled variable; a comment says so).
- isbn: an agent briefly edited the evaluated attempt-001 and restored it byte for byte (hash matches).
- The brief or description is ambiguous in: jobs_puzzle (clue 5), crossword (order of `E`),
  session3_exodus (which list is numbered canonically), football (units), best_host (minimise or satisfy).
- kakuro json:4 carries the full solution grid in a `note` key. The model does not read it.
- Deleted by hand: a stray `probe/` directory (flow_free_game) and an empty attempt-002 directory
  (futoshiki). futoshiki attempt-001 is an unevaluated draft.

## Process

Up to 20 agents ran at once, one problem each. Killing a `docker run` client leaves the
`eclipse.exe` container running (it ignores SIGTERM). A few probe containers were still running
at the end; `docker ps` lists them.
