# AGENTS.md

## Workflow

- For each new feature or bug fix, always create a new branch and start coding there.
- Make appropriate commits on that branch, but never push — the user handles all pushing.
- Group a batch of related work into one commit rather than committing each file or each
  generated model on its own, and say in the message what the batch carries.
- After coding is done, the user and the agent review whether the request is done.

## This repository

It holds the problems only: `dataset/`, their sources in `SOURCES.md`, and the tooling
that reads them. New problems follow `CONTRIBUTING.md`, and `python -m unittest
tests.test_dataset` is the audit CI runs.

Generated models, the evaluator, the solver integrations, the agent skills and the
catalogue live in [DCP Rosetta](https://github.com/DCP-Bench/DCP-Rosetta), which checks
this repository out as its `bench/` submodule. Model generation and instance curation
run from there: follow its `skills/model-generator` and `skills/instance-curator`.

