# Cheapest committee, all optimal choices (all optimal solutions)

**Problem:** choose 3 of 6 candidates at minimum total cost, with at least one from group A (0..2) and one from group B (3..5).
**Shows:** the all-optimal pattern: solve for the optimum, build a second model with the objective fixed to the optimum (`cost == optimum`) and no objective, then enumerate the decision variables. Also `AddBoolOr` and a sum constraint on Booleans.
**Run:** `cmake -S . -B build && cmake --build build && ./build/model`
**Expected:** `Optimal cost: 8`
**Expected:** `Optimal choices: 3`

Needs `CMAKE_PREFIX_PATH` pointing at the OR-Tools folder; see the skill's Install section. The second model is built from scratch, because a model that still carries the objective would be optimised again rather than enumerated.
