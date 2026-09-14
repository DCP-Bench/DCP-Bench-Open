# csplib_005_autocorrelation

A +/-1 sequence of length n minimising the energy sum of squared periodic
autocorrelations E = sum over s in 1..n-1 of PAF(s)^2.

- Instance input: `n`. Output: `sequence` — n integers that are -1 or 1.
- Minimize E. The reference's `sequence != 0` is what makes the domain +/-1.
