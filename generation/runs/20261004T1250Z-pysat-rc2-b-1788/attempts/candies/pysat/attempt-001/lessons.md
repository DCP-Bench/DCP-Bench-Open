# Lesson: an output Integer must not use the pure order encoding

This attempt declared the outputs `x` and `z` as `Integer(..., encoding="order")`.
The first solution was emitted, then the runner failed with
`execution_error: Direct encoding is disabled` (see `evaluation.json`): to
enumerate, the runner blocks an answer with `-leaf.equals(value)`, and
`Integer.equals` needs the direct literals.

Attempt 002 changed only the encoding to `"coupled"` and was accepted on all
five instances.

Proposed skill text: an `Integer` placed in `outputs` must use `"direct"` or
`"coupled"`; `"order"` is fine only for internal variables.
