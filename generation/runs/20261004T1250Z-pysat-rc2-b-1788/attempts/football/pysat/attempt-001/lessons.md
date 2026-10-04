# Lesson: PBEnc refuses a negative bound

`PBEnc.equals(..., bound=-28310, encoding=EncType.adder)` failed in the image with
`execution_error: Wrong bound: -28310` (see `evaluation.json`). Negative weights are
accepted, a negative bound is not. Attempt 002 negated the equation so the bound is
non-negative.

Proposed skill text, beside "PBEnc accepts negative weights": the bound must be
non-negative; move terms across or negate the whole equation to get there.
