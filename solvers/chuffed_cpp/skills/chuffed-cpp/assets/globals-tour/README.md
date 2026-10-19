# Globals tour (satisfy)

**Problem:** small independent puzzles in one model: a 4-node tour, an allowed-pairs table, three tasks on 2 workers of which two share a machine, a 4-symbol sequence without two consecutive 2s, and three Booleans of which at least two hold.
**Shows:** `circuit`, `table` with tuples built in place (`t.push(); t.last().push(v)`), `cumulative`, `disjunctive`, `regular` (DFA with 1-based states and symbols, 0 rejects), `bool_clause`, `bool_linear` with `getConstant`, and branching on Booleans through `bool2int`-linked 0..1 `IntVar`s.
**Run:** `cmake -S . -B build -DCMAKE_BUILD_TYPE=Release && cmake --build build && ./build/model`
**Expected:** `succ = 1 2 3 0; ab = 0 1; s = 0 2 0; seq = 1 1 1 1; bs = 0 1 1`

Without the `bool2int` link in the branch, the Booleans stay unfixed in the reported solution and read `0 0 0`, which breaks "at least two hold" (also with `so.vsids = true`).
