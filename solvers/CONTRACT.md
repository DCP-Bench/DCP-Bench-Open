# The submission contract

What every model submitted to DCP-Bench Open must do, whatever the solver, language or
framework. Each integration realises it in its own terms, documented in
`solvers/<id>/CONTRACT.md`. Read this file first, then the integration's contract, then
the solver skill for the API.

A submission is checked against a trusted reference
(`dataset/<problem>/<problem>.cpmpy.py`) by the evaluator ([evaluation/README.md](../evaluation/README.md)).
`python -m generation.brief PROBLEM` prints the facts this contract refers to: the declared
outputs and their shapes, the objective direction, and every instance field with its shape.

## Input: one instance

- The model receives **one instance**: a JSON object whose fields and shapes the brief
  lists. Field values are integers, Booleans, strings, or arrays of these, possibly nested
  and possibly ragged (`unbindable_fields` in the brief names the ragged or mixed-type
  ones).
- The same model is run on **every instance** of the problem. Read every quantity from the
  instance: sizes, data, bounds that depend on data. Fixed mathematical constants are
  fine; a number that happens to be right for the example is not.
- **Never embed an answer**, whether computed by running the reference, copied from it, or
  chosen by recognising which instance you were given.
- An instance may carry extra keys the brief does not list (`name`, `note`). Ignore them.

## Output: the declared outputs

- The model exposes a mapping from **each declared output name** to a value of the
  **declared shape** (a scalar, or a nested array with exactly the declared dimensions).
  Exactly those names: none missing, none extra.
- Every leaf is an **integer or a Boolean**. Floats and strings are rejected, never
  coerced; a Boolean may also be given as 0/1.
- The model may use any number of **auxiliary** variables. They stay private: only the
  declared outputs are reported, and two solutions count as **distinct only if they differ
  in a declared output**.

## Objective

- The brief gives the direction: satisfaction, minimize, or maximize.
- A satisfaction problem declares no objective. An optimisation problem declares **one
  integer objective** with that direction, built from the model's variables.
- Do not bound the objective yourself (no `objective <= k` from a known optimum, no search
  for it in your own loop): proving the optimum is the runner's job.

## The runner's side

The integration's runner, not the submission, does the solving:

- It builds the model from the submission, solves it, and for an optimisation problem
  **proves the optimum** before reporting anything. A solution whose optimality was not
  proven within the time limit is reported as `timeout`, never as a result.
- To return several solutions it **pins the optimum** (for optimisation) and enumerates
  further solutions that differ in a declared output, up to the requested count. Fewer
  solutions than requested are fine only when the search space is exhausted.
- It serialises the declared outputs and reports one final status.

So a submission **declares a model and nothing else**: it does not call the solver, print to
stdout, read or write files, take command-line arguments, or define its own `main`. Only the
one submission file is staged in the container; it cannot import a helper file of its own.

## What the reference does not license

The reference is the specification, and translating its semantics is the work. But:

- never execute its solve tail;
- never carry over a constraint it keeps **commented out** between
  `<SYMMETRY_BREAKING_CONSTRAINT_START>` and `<SYMMETRY_BREAKING_CONSTRAINT_END>`;
- a missing or self-contradictory specification is a reference blocker to record, not
  something to work around.

## How it is checked

`python -m generation.manage evaluate --attempt ATTEMPT --model MODEL` runs the submission on
the run's instances and checks every reported solution against the reference. It looks for
a counterexample; an accepted model is one for which none was found.

| `reason` | Meaning |
|---|---|
| `invalid_solution` | A reported solution violates the reference: the model is wrong or under-constrained |
| `suboptimal_solution` | A reported "optimal" solution is not optimal for the reference |
| `no_solution` | The model reported no solution where the reference has one (over-constrained, or wrong) |
| `invalid_output` | The reported outputs do not match the declared names or shapes, or too few distinct solutions without exhaustion |
| `output_limit` | Too much output (8 MiB per stream) |
| `compilation_error` | A compiled submission did not compile |
| `execution_error` | The submission raised or crashed, or the runner could not read it (a missing entrypoint, a float or string output leaf); read `detail` |
| `execution_timeout`, `memory_limit` | Inconclusive; solutions checked before it were all accepted |
| `reference_timeout`, `reference_error`, `infrastructure_error` | Not the submission's fault |

## Mapping checklist

Every `solvers/<id>/CONTRACT.md` answers these, under these headings, so a modeller can map
this contract onto the integration, and solver-setup knows what a new runner must define:

| Heading | Question |
|---|---|
| `## Submission file` | Which file is submitted (extension), and what may it contain or import? |
| `## Entrypoint` | Which function, predicate or item does the runner call or read, with what signature? |
| `## Instance` | In what form do the instance fields arrive (types, index base, strings, name changes)? |
| `## Outputs` | How are the declared outputs handed back (container, keys, allowed value kinds)? |
| `## Objective` | How is the objective declared, and what form must it take? |
| `## Compilation` | Is the submission compiled, and under which budget? |
| `## Environment` | Image, language and solver versions; what is available to import |
| `## Traps` | What this integration rejects or mishandles that the generic contract does not predict |
| `## Example` | A minimal complete submission (the integration's pilot fixture) |
