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
  - `memory_limit` — your model ran and the kernel killed a process in its
    container at the memory limit. Read it as `execution_timeout`: usually an
    encoding too large for the instance, reported the same way.
- `solutions_checked` is at least 1 and within the requested limit.
- The retained `model_hash` matches the bytes you wrote.

Reduced coverage is acceptable **only** when the cause is a recorded reference or
infrastructure limit. If the failure is the model's, the model is wrong; fix it.

## The check the evaluator cannot do

Most problems in this corpus have only the embedded example, so there is no
second instance to expose a model that simply hardcoded the first one. The
retained record says so in `evaluation.instances_available`, and `next_work`
reports `instances` per pair.

So before retaining, read your model and confirm every quantity that belongs to
the instance is taken *from* the instance argument, not typed in. A model whose
`build` never reads its argument has hardcoded the example, whatever the
evaluator said. This has happened here: the first accepted model, for
`abbots_puzzle`, hardcodes all its constants and passed, because that problem
has exactly one instance.

A constant that belongs to the *problem* rather than the instance — a nutrient
table the reference itself fixes, a domain bound it declares — may be mirrored,
but say so in a comment where it appears.

## The model has to be readable

A model in this corpus is read by people comparing how frameworks say the same
thing. One that is merely correct fails at that job, so **before retaining,
confirm every constraint group carries a comment saying what it means in the
problem's own words**, and that the file opens with a line stating what the
problem is.

Use the vocabulary of the problem statement, not of the encoding. The reference
models do this and are the standard to match. `capital_budget`'s reference says:

```python
x = boolvar(shape=n, name="x")  # x[i] = 1 if investments i
z = intvar(0, sum(npv), name="z")  # total NPV
model = Model([
    # the sum of all choosen investments must be less than the budget
    sum(x * cash_flow) <= budget,
    z == sum(x * npv)
])
```

A generated model for the same problem that names `chosen` and `total` and
posts the two constraints with no comment at all is correct and unreadable;
a reader has to reconstruct which line is the budget and which is the payoff.

Two things are worth a sentence of their own wherever they appear, because
neither is recoverable from the code: **where a bound comes from** (the
instance field, the problem statement, or a derivation you did), and **why an
encoding was chosen** when a more obvious one exists. A workaround for a
framework limitation should name the limitation.

This is not something the evaluator or any test can judge — a comment count
cannot tell the reference's wording from `# constraint 1`. It is yours to
check, on the same reading pass that checks for hardcoded data.

The evaluator also never proves a model is *right*: an overconstrained model
leaves no trace in the outputs it examines. A model that passes every instance
may still be narrower than the problem. That judgement is yours.
