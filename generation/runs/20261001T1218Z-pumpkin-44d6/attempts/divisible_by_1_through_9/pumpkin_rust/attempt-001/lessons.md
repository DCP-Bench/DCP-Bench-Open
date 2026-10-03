The declared output is the ten-digit number (the reference answer is above 2^31 - 1).
Pumpkin variables, `Instance` integers and `Node::ConstInt` are all `i32`, so no output can carry it.

Attempt 001 caps the last prefix at `i32::MAX` and posts `t9 = 10 * t8 + x9` with `t8` in 0..999999999.
At run time the process panicked inside pumpkin-core (`conflict_analysis_context.rs:117`, "all predicates
in the conflict nogood should be assigned to true") instead of reporting unsatisfiable. Suspected cause,
not confirmed: `scaled(10)` on a variable whose bound times 10 exceeds `i32`. If so, a linear term whose
coefficient times bound overflows `i32` makes the process panic rather than return an error.
