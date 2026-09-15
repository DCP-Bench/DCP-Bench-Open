# Deciding a model is correct

Acceptance is a search for a counterexample that came back empty. That is worth
something, and it is not proof. Before retaining, confirm all of this from the
evaluation record itself, not from your own expectation.

## What the record has to say

- `accepted` is `true` and the reason is `accepted`.
- `unperformed_instances` is empty. Without `tolerate_inconclusive`,
  `instances_checked` equals `min(profile instance_count, instances_available)`;
  with it, read `skipped_instances` and check the reason on each one, because
  the two timeouts mean opposite things:
  - `reference_timeout` — the reference itself could not be solved. Nothing
    about your model is implicated, and no amount of repair will help.
  - `execution_timeout` — your model ran and *your* solver was too slow. That is
    a repair signal: a missing bound, a weak encoding, an implied constraint the
    solver cannot derive, or a framework that is the wrong tool for this
    problem. Tolerating it is legitimate, but report it as a performance limit
    rather than implying the problem was blocked, and say which instances the
    model is actually evidenced on.
- `solutions_checked` is at least 1 and within the requested limit.
- The retained `model_hash` matches the bytes you wrote.

Reduced coverage is acceptable **only** when the cause is a recorded reference or
infrastructure limit. If the failure is the model's, the model is wrong; fix it.

## The check the evaluator cannot do

Most problems in this corpus have only the embedded example, so there is no
second instance to expose a model that simply hardcoded the first one. The
retained record says so in `generality.example_only`, and `next_work` reports
`instances` per pair.

So before retaining, read your model and confirm every quantity that belongs to
the instance is taken *from* the instance argument, not typed in. A model whose
`build` never reads its argument has hardcoded the example, whatever the
evaluator said. This has happened here: the first accepted model, for
`abbots_puzzle`, hardcodes all its constants and passed, because that problem
has exactly one instance.

A constant that belongs to the *problem* rather than the instance — a nutrient
table the reference itself fixes, a domain bound it declares — may be mirrored,
but say so in a comment where it appears.

The evaluator also never proves a model is *right*: an overconstrained model
leaves no trace in the outputs it examines. A model that passes every instance
may still be narrower than the problem. That judgement is yours.
