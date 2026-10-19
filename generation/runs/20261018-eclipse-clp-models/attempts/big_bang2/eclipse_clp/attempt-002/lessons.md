# big_bang2 on eclipse_clp, retry: attempt-002 lessons

Model: counts view per die (`Counts[V]` = faces showing V, `Below[V]` = faces below V, `sum(Counts) #= 6`,
`sum(V*Counts[V]) #= face sum`), one product `P #= C*B` per (winner value, loser below) and `sum(Ps) #>= 19`
per beats relation (10 relations). Search: per die (Rock, Scissors, Paper, Lizard, Spock) a closeness
variable, then its counts, then all faces; `search(Vars, 0, input_order, indomain_max, complete, [])`.

Not evaluated through `manage evaluate`: the free check (`evaluation.check`, one instance, 180 s) hit
`execution_timeout` ("budget ran out during search"), so the model cannot be accepted as it stands.

Standalone timing probes (main that calls `model/3` then `search_goal/1`, run in the image with `--ulimit cpu`):
- ic, closeness as `Cl #= 33 - abs(S - 39)`, with products and beats: no first solution in 200 s, 290 s.
- ic, same with a linear deviation (`S - 39 #=< Dev`, `39 - S #=< Dev`, `Cl #= 33 - Dev`) and the weighted-sum
  redundant constraint: no first solution in 170 s.
- ic, same without the beats sums (`wins` reduced to the products): no first solution in 170 s.
- ic, no beats constraints, closeness variables NOT in the search (counts and faces only): first solution at once.
  So the stall comes from labelling the closeness variables first, not from the beats sums alone.
- gfd, the same model with `(F #= V) <=> (B #= 1)`: no first solution in 200 s.
- ic, the closeness variables labelled with `indomain_min` instead of `indomain_max`: no first solution in 130 s.

Reading: with the closeness variable labelled, a count vector whose weighted sum is wrong seems to be detected
only after the faces are labelled (the face sum is not pruned from the counts), so the search explores faces
under wrong count vectors. Not verified; a probe that posts the face sum through the faces' domains, or a
search that labels faces before counts, is the next thing to try.

The hint's figure (2 solutions in 1.40 s for the closeness order) was not reproduced with these variants. The
differences from the tested model are unknown. Do not spend another evaluated attempt on the same search order.

Next attempt candidates (untested): labelling faces die by die with the closeness only as a value order on the
face sum; search over the counts with `first_fail`; gfd `count/4` for the counts.
