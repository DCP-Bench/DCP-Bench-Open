# general_store, cvc5_python, attempt-005 (retry round)

Result: rejected, execution_timeout. The runner found the first solution (S=0, unique in the description) and the second check (unsat proof) timed out at 180 s.

Encodings tried with `SolverFor("QF_LIA")`, no leading-nonzero rule, check at 180 s each:

| variant | first solution | second check |
|---|---|---|
| one-hot digit Booleans, exactly-one per letter and per digit, carries <= 15 | no (timeout) | not reached |
| same plus redundant sum of letters = 45 | no (timeout) | not reached |
| Int letters 0..9, pairwise `!=`, no Booleans | yes | timeout |
| one-hot per letter, value channel, no per-digit exactly-one, pairwise `!=` | no (timeout) | not reached |
| one-hot per letter + per-digit exactly-one + pairwise `!=`, carries <= 15 (this file's model is this variant) | yes | timeout (rejected in full evaluate) |
| same as above plus sum-45 row | no (timeout) | not reached |
| same as above with per-column carry bounds from the word lengths | no (timeout) | not reached |

Lessons:
- The hint's 79 s first-solution / 0.8 s second-check figures did not reproduce in the container. The hint's model kept the leading-nonzero rule for C, B, A, P, H; the description does not state it, so it was not used.
- The redundant sum-45 row and tighter per-column carry bounds made the first solution slower. Both are probably neutral to harmful here.
- Refutation (second check) is the bottleneck. Pairwise `!=` on Int letters found the first solution but gave no quick unsat proof; per-digit exactly-one Booleans did not rescue it.

Untried ideas: a finer one-hot form for the carries (Boolean per carry value), or a derived lower bound for A from the leading column (A = P + carry_6), which the solver should derive anyway.
