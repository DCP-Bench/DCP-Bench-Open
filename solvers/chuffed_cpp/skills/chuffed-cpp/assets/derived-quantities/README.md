# Derived quantities (satisfy, several solutions)

**Problem:** three numbers in 0..n (n from the command line, default 4) with a weighted-sum limit, an implication and a lexicographic order, plus quantities derived from them.
**Shows:** one `IntVar` per intermediate with a defining constraint: `int_minus` + `int_abs`, `maximum`, `int_min`, a reified count (`int_rel_reif` + `bool2int` + `int_linear`), `int_rel_half_reif`, weighted `int_linear` with a bound and with a result variable, a 2-D table lookup (row-major `array_int_element` with `idx = 3*r + c`), `lex`, and `so.nof_solutions = 3` with `output_vars`.
**Run:** `cmake -S . -B build -DCMAKE_BUILD_TYPE=Release && cmake --build build && ./build/model`
**Expected:** `x = 0 0 0, ad = 0, hi = 0, lo = 0, cnt = 0, lt = 0, wsum = 0, val = 5`
**Expected:** `x = 0 0 2, ad = 0, hi = 2, lo = 0, cnt = 1, lt = 0, wsum = 6, val = 5`
**Expected:** `solutions 3`
