attempt-001 posted each of the four non-overlap cases with
`addLeftReification(case, True, [(1, coords[second]), (-1, coords[first])], sides[first])`,
reading the skill's comment `addLeftReification(...)  # head -> constraint`, and at least one case
true. The evaluator rejected the first solution (invalid_solution, "Declared outputs cannot extend
to a reference solution", evaluation.json in this directory). attempt-002 changed only the call to
`addReification` (head <-> constraint, the form the skill marks as verified) and was accepted.
The skill documents the one-way forms without a verification, so the direction of
`addLeftReification` / `addRightReification` is unconfirmed and may be the reverse of the comment.
