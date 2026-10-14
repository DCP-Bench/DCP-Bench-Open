An `Integer` with `encoding="order"` cannot be a declared output: the runner blocks a
reported answer with `leaf.equals(value)`, and `equals` on an order-only Integer raises
`Direct encoding is disabled` (evaluation.json here, and cabling attempt-001). Outputs
need `"direct"` or `"coupled"`; `"order"` is fine for auxiliaries the objective charges.
