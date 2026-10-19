# Lessons: divisible_by_1_through_9 on pindakaas_rust

Result: execution_error, "Rust process exited -6" (C++ bad_alloc: "memory allocation of 72000000000 bytes failed").

The model encodes the problem correctly as far as the check shows: a permutation of the digits 0 to 9 with a nonzero leading digit, and a remainder chain per n (R_k = (10 R_(k-1) + d_(k-1)) mod n, R_n = 0). It is not a formulation problem.

The cause is the output. `number` is a 10-digit value, so its integer variable has a domain of about 10^10. The harness gives every integer output an equality view (`x.equals(min)`), and it blocks each solution with `x.equals(v)`. Both build a direct encoding with one literal per domain value, which is impossible at that width.

A bare `IntVar::new(0..=9999999999)` output fails the same way, so the output representation is the cause, not the arithmetic. A binary-encoded variable (`IntVar::from_binary_encoding` over 34 literals, then `constrain`) ended in a foreign C++ exception ("Rust cannot catch foreign exceptions, aborting"), so it is not a workaround either.

Blocked: the integration has no wide-output mechanism. The contract's Outputs section says a wide value needs one (for example digit outputs) and names none for this integration.
