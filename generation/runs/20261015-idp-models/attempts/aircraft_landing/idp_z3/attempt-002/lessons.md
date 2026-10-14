`if c then a else b` inside a `sum{{ ... | p in Plane }}` parses and solves in IDP-Z3 0.12.1, and the `i < j` comparison on a `<: Int` type works for pairwise constraints.
Bounded `-> Int` decisions (time windows as constraints) solved all five landing instances; the two largest hit the solution limit rather than the timeout.
Attempt-001 was accepted but had a comment that misdescribed a pairwise constraint as consecutive; attempt-002 changed only that comment and was re-evaluated.
