# AGENTS.md

## Workflow

- For each new feature or bug fix, always create a new branch and start coding there.
- Make appropriate commits on that branch, but never push — the user handles all pushing.
- Group a batch of related work into one commit rather than committing each file or each
  generated model on its own, and say in the message what the batch carries.
- After coding is done, the user and the agent review whether the request is done.

## Writing models for this benchmark

*Rosetta* is this repository's model collection and the machinery that writes and checks
it (see the README). Skills in `rosetta-skills/` work only here; skills in `skills/` and
the solver skills in `solvers/<id>/skills/` must work anywhere.

Follow `rosetta-skills/model-generator`, which runs a
campaign end to end, and `rosetta-skills/solver-setup` for adding a framework/solver.
Follow `rosetta-skills/instance-curator` to add instances to existing problems. A generated model should be kept only when the evaluator accepts it.

`python -m generation.brief PROBLEM` prints what a model has to satisfy: the problem
description, the declared output names with their shapes, the objective direction, and
every instance field with its shape. Modelling starts blind, from the brief, the
contracts and the solver skill, without the reference (see `rosetta-skills/model-generator`). `python -m generation.next_work` says what is left, and withholds pairs whose
instance shape an integration cannot bind at all.

