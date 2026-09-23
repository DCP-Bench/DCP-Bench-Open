# generation

Bookkeeping for models written by an agent rather than by hand.

The agent itself is not here — it lives in `skills/`. This package only keeps
the records that make a generated model trustworthy: what was attempted, what
the evaluator said, and whether an integration was in a state to be trusted at
all. No module calls an LLM or decides what to model.

| Module | What it does |
| --- | --- |
| `next_work` | Lists what is left to model, and which integrations are usable right now. |
| `readiness` | Certifies an integration: runs its own checks and binds the result to its image and files. |
| `manage` | The run ledger — create an attempt, evaluate it, keep it if it passed. |
| `instances` | Gates a new instance before it joins the dataset, and rechecks retained models on it. |
| `skills` | Validates a skill bundle, and reviews proposed changes to one. |
| `behaviour` | Runs a skill's behavioural evals. |

## The two commands worth knowing

What is left to do, and what can do it:

```sh
python -m generation.next_work
```

It reports each integration as usable or blocked, how many problem/solver pairs
already have an accepted model, and which pairs to try next — largest problems
first, because a model that hardcoded the example is caught by a second
instance rather than by review.

Whether an integration can still be trusted:

```sh
python -m generation.readiness verify --solver z3_python --record solvers/z3_python/readiness.json
```

A record ties an integration's image to the checks that were actually run
against it. Change the runner, the Dockerfile or the checks and the record
stops verifying, and the integration drops out of the queue until it is
re-certified. That is the mechanism behind "an accepted model means something".

## Where the records live

`generation/runs/RUN/` holds one campaign: a manifest, an event log, and one
directory per attempt with the candidate and the evaluator's verdict —
including the attempts that failed, which is most of what makes the ledger
worth reading. Accepted models are copied to `generated_models/` and keep their
verdict in `record.json`.

`generation/blockers.json` lists pairs not worth retrying, each with the
evidence that justifies it, so the same dead end is not rediscovered.

`generation/flags.json` lists retained models that failed an instance added
after they were accepted, with the evaluator's evidence. A flagged model stays
where it is and is marked on the site, but no longer covers its pair.

## For agents

[AGENTS.md](AGENTS.md) is the full contract: exact command syntax, record
schemas, and the rules that do not bend. Read that one before running anything
here.
