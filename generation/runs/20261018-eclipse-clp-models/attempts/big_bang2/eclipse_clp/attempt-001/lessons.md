# big_bang2 on eclipse_clp: lessons

Model: 5 dice x 6 faces in 1..12, one reified flag per face pair (X #> Y), `sum(Flags) #>= 19` per beats relation (10 relations).

Free checks (evaluation.check, one instance, solution limit 2, 150 s), none evaluated through `manage evaluate`:
- ic, faces and flags labelled (first_fail, indomain_min): execution_timeout, "budget ran out during search". Earlier run also reported `Declared outputs cannot extend` because the reification lacked `param(X)` in the inner foreach; fixed.
- ic, faces only, first_fail/indomain_split: execution_timeout.
- ic, faces only, smallest/indomain_min: execution_timeout.
- ic, faces only, input_order/indomain_min: execution_timeout.
- ic, faces only, first_fail/indomain_max: execution_timeout.
- gfd, faces only, first_fail/indomain_min: driver outlived budget.

The reified sums propagate weakly, so search over 30 face variables does not finish within 150 s for any tried order. Not tried: sum-of-count encodings, face ordering (would be symmetry breaking not asked for), stronger decompositions of the beats relation.

Reference was not read (blind modelling).
