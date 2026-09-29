# DCP-Bench-Open Sources

The dataset contains problems gathered from different sources.

- `aplai_course`: Problems from the APLAI course of KU Leuven, 2023-2024. As modelled here: https://github.com/kostis-init/LLM-CP-Modeling/tree/main/data/APLAI_course
  - All 18 problems are added.
- `complex_or`: Problems from the ComplexOR repository, found here: https://github.com/xzymustbexzy/Chain-of-Experts
  - Those already modelled in other folders (e.g. knapsack) and those with heavy float parameters/objective values are excluded.
- `cpmpy_examples`: Problems from the cpmpy examples folder, https://github.com/CPMpy/cpmpy/tree/master/examples
  - All included, except for the ones that require enumeration of all solutions (e.g. `solveAll`).
- `csplib`: Problems from the csplib, https://www.csplib.org/Problems/
  - For now, only the ones modelled in the cpmpy repository are included (https://github.com/CPMpy/cpmpy/tree/master/examples/csplib), and the ones modelled by Hakan Kjellerstrand (http://www.hakank.org/cpmpy/).
- `hakan_examples`: Models created by Hakan Kjellerstrand, http://www.hakank.org/cpmpy/
  - In progress with alphabetical order. Currently, includes all problems until `knights_tour_circuit.py`, excluding the following:
    - Those already modelled in other folders (e.g. aplai_course, cpmpy_examples, csplib)
    - Those that contain `solveAll` (counting solutions).
    - Global constraints tests, e.g. http://www.hakank.org/cpmpy/atmost_test.py

## Generated models

`generated_models/<problem>/<framework>/<submission>/` holds models produced by
generative systems, not ground truth. Every one was generated in this repository
by the `model-generator` skill against an integration under `solvers/`, and kept
only because the evaluator accepted it.

Each model directory holds the model and one `record.json`. Its `verdict_source`
is `container_evaluator`, and the evaluator's full result is embedded in the
record. `generation/runs/` holds how each model was made.

Two other corpora used to live here: one imported from the CP-Bench leaderboard,
and a set of abbots-puzzle demo models written across frameworks that have no
integration here. Neither was judged by the evaluator in this repository, so
neither counted as coverage, and both have been removed.

## Instances not added

Problems judged unable to take another instance, one line each as
`` - `problem`: reason ``. `python -m generation.instances status` reads this
list and stops offering them. See `skills/instance-curator`.

- `session2_color_simple`: the description names the six countries, so geography fixes the graph.
- `who_killed_agatha`: the description fixes the whole scenario, and the reference never reads its only field.
- `csplib_018_water_bucket`: the description fixes the buckets, the start and the goal.
- `csplib_023_magic_hexagon`: the description fixes the numbers 1 to 19, the layout and the sum 38.
- `csplib_011_acc_basketball_schedule`: the description fixes all the data: nine named teams, 18 dates and the fixed matches.
- `three_coins`: the description fixes the starting coins and the number of moves.
- `curious_set_of_integers`: the description fixes the set, and every bound gives the same answer.
- `flow_free_game`: the description prints the one board it uses.
- `dudeney_numbers`: no Dudeney number has more than 6 digits, so only n below 6 changes the answer, and the reference exceeds 10 s at n = 4 and 5. Stays at 2.
- `csplib_026_sports_tournament_scheduling`: n = 4 has no solution and n = 10 or more exceeds 10 s. Stays at 2.
- `csplib_049_number_partitioning`: n must be a multiple of 4 and at least 8; 8 to 16 are listed, and from n = 20 the reference takes more than 30 s. Stays at 3.
- `calvin_puzzle`: n = 2 to 4 have no solution, n = 1 has no moves, and from n = 7 the reference takes more than 60 s. Stays at 2.

## Dataset decisions

Some changes made to the source problems (many more may have been made), and the reasoning behind them.

**Removed as provably unsatisfiable.** QG3 quasigroup orders m in
{2,3,5,6,7,10,11,14,15,18,19}, and perfect-square-placement `problem3`. For the
QG3 identity `(a*b)*(b*a)=a`, a necessary condition is m congruent to 0 or 1
modulo 4; order 5 is also impossible. See
[Fujita, Slaney and Bennett, IJCAI 1993, page 55](https://www.ijcai.org/Proceedings/93-1/Papers/008.pdf).
A reference with no solution cannot judge a candidate. A deterministic test
checks this necessary condition on the retained orders; it does not establish
that every retained instance is satisfiable.

**Translated.** The nonogram reference was moved from an OR-Tools native
automaton to CPMpy's `Regular` constraint. Equivalence was established by
solving all 14 listed instances and re-checking each board against the
row/column block rules — by testing, not by proof.

**Corrected.** The bin-packing reference applied the capacity limit to one bin
per item (`range(n)`) rather than to every bin (`range(num_bins)`), so with more
bins than items the extra bins were unbounded. No listed instance has more bins
than items, and on those the two versions accept exactly the same solutions.

**Removed as too slow for the reference.** The reference runs on one CP-SAT
worker with dual presolve reductions off, which on some models is several times
slower than CP-SAT's defaults. An instance stays only if the reference finds a
solution, or proves the optimum, within 30 s, half the evaluator's default 60 s
reference limit. Each instance was timed once, and three times if it took more
than 15 s; these took more than 30 s in at least one run and were removed. The
indices are the `json:<index>` IDs they had before the removal:

- `csplib_001_car_sequencing`: 53 of the 75 instances, `json:1`-`4`, `6`, `8`,
  `13`, `15`, `16`, `18`, `23`, `26`, `28`, `29`, `31`, `36`-`56`,
  `58`-`74`.
- `csplib_002_template_design`: `herbs2`, `herbs3`, `magazine_inserts2`,
  `magazine_inserts3`, `magazine_inserts4`.
- `csplib_003_quasigroup_existence`: orders m = 12, 13, 16, 17 and 20.
- `csplib_009_perfect_square_placement`: `problem8` (base 110, 22 squares).
- `csplib_010_social_golfers_problem`: 7 weeks of 7 groups of 7, and 9 weeks of
  8 groups of 8.
- `csplib_013_progressive_party_problem`: `csplib_example` (42 boats, 6
  periods), where the reference finds no solution within 60 s.
- `csplib_032_max_density_still_life`: the 9x9 and 10x10 boards.
- `csplib_044_steiner`: n = 15.
- `csplib_049_number_partitioning`: n = 20.
- `calvin_puzzle`: `7 by 7`.

**Reformulated for speed.** Two references were changed without changing
their solutions. The cmo_2012 reference states that p is prime with
`InDomain(p, prime_list)` instead of a sum of 1,229 equalities; on the embedded
example it goes from 89 s to 5 s on one CP-SAT worker, with the same optimum on
all five instances. The template-design reference adds the implied bound
`n_slots * sum(production) >= sum(demand)`, which holds for every solution
because each template fills all its slots; `catfood3` goes from over 60 s to
2 s, and the example keeps its optimum of 418.

**Retained as they appear in the source.** Named duplicates of an embedded
example (nonogram `bear`, template-design `catfood2`, perfect-square-placement
`problem2`). The evaluator deduplicates by declared data fields and ignores
metadata: the embedded example takes precedence, otherwise the first JSON
record is kept with its metadata and original `json:<index>` ID.

