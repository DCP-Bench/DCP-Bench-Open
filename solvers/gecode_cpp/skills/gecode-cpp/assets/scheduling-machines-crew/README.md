# Parallel machines with a shared crew (scheduling)

**Problem:** six tasks with durations, release times and crew needs run on 2 identical machines (one task at a time each) and share a crew of 3; minimise the makespan.
**Shows:** optional `unary` per machine with Booleans linked by a one-hot `channel`, `cumulative` for the crew, `max` for the makespan, `precede` for interchangeable machines, start-time branching (`INT_VAR_MIN_MIN`), `RBS<T, BAB>` with `Search::Cutoff::luby(100)`.
**Run:** `g++ -std=c++17 -O2 model.cpp -o model -lgecodesearch -lgecodeminimodel -lgecodeset -lgecodefloat -lgecodeint -lgecodekernel -lgecodesupport && ./model`
**Expected:** `Makespan: 8`

8 is the work bound (15 units of work over 2 machines is 7.5, rounded up), so it is optimal; proven in under 0.01 s on Gecode 6.2.0.
