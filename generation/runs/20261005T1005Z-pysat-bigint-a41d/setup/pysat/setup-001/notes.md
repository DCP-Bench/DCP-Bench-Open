# pysat: outputs declared as a LinearExpr

An `Integer` registers one variable per value, so a ten-digit output
(divisible_by_1_through_9) or one near 4.6 million (fibonacci_even) was killed at
the 2048 MB limit before any constraint was added. Both pairs were blocked as
`unsupported_value_range`.

Change in `solvers/pysat/run.py`: an output leaf may be a
`pysat.integer.LinearExpr` over Integers. The runner evaluates it from the
assignment, blocks the summed Integers when enumerating, and skips a repeated
declared output instead of emitting it twice (that guard applies to every
output type).

Readiness gains `wide_output` (2**33 + n through 35 0..1 Integers) and
`repeated_output_once` (a + b over two 0..1 Integers: one distinct output,
status complete). All 17 checks pass; the record verifies; the pysat pilot tests
(`test_pilots`, `test_maximization`, metadata tests) pass with
`DCP_CONTAINER_TESTS=1`. The modelling skill documents the pattern and validates.

Not verified: the skill's evals were not run by a separate agent.
