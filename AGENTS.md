# AGENTS.md

## Workflow

- For each new feature or bug fix, always create a new branch and start coding there.
- Make appropriate commits on that branch, but never push — the user handles all pushing.
- After coding is done, the user and the agent review whether the request is done.
- Once the request is accepted, the user handles deployment.

## Writing models for this benchmark

Follow `skills/model-generator`, which runs a
campaign end to end, and `skills/solver-setup` for adding a framework/solver. A generated model should be kept only when the evaluator accepts it.
