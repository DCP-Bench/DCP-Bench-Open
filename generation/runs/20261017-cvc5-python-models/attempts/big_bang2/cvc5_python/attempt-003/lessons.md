# big_bang2 lessons (cvc5_python)

Outcome: no instance verified. Evaluation rejected with `no_instance_verified`
("Every selected instance was inconclusive"), the single instance `example` hit
`execution_timeout` (180 s) with no solution reported.

Attempts:
- attempt-001: 5 dice x 6 faces as Int in 1..12, one `Sum(If(a > b, 1, 0))` over 36
  face pairs per beats relation, `> 18`. `evaluation.check` timed out at 180 s.
- attempt-002: purely Boolean. Order encoding per face (threshold Booleans 2..12),
  reified face-pair comparisons, sequential counter for "at least 19 of 36". Timed out.
- attempt-003: as attempt-002 with one-directional (polarity) reification. Timed out
  in `evaluate` as well.

Reading: the constraint structure is small (60 face values, 10 threshold counts over
36 comparisons), but none of the three encodings reached a first solution within
180 s on cvc5. The search space for the face values is large and the solutions are
hard to reach by propagation. Dropping reification direction and switching to a pure
Boolean encoding did not change the outcome.

Not tried: symmetry breaking within dice or across dice (forbidden by the contract
unless the description asks for it). Not tried: any change to the solver logic or
options (the runner ignores them, per the known gap in the cvc5 coordinator note).
