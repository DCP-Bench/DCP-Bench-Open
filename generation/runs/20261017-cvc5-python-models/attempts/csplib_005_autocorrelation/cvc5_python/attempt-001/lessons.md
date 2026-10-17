# attempt-001 lessons (csplib_005_autocorrelation, cvc5_python)

Rejected: `suboptimal_solution` on `example`, "Declared outputs cannot achieve the reference optimum".

Cause: the square table bounded C_k by n-k. In the periodic energy every one of the n products
contributes to C_k, so |C_k| <= n. Values above n-k were excluded, which cut off the true optimum.
Fix in attempt-002: table over -n..n.

Diagnostic (free checks, not attempts): replacing the Bool equality with Xor and keeping the
bound n-k gave the same rejection; swapping to c*c (nonlinear) with the Bool equality was accepted
in 21 s on example. The table bound was the fault.
