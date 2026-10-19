# Subsets with a given sum (all solutions)

**Problem:** list every subset of {2, 3, 4, 5, 6, 7} whose sum is 10.
**Shows:** Boolean decision variables, a linear sum constraint, enumeration with a solution observer and `set_enumerate_all_solutions`, the single-worker setting that enumeration needs.
**Run:** `cmake -S . -B build && cmake --build build && ./build/model`
**Expected:** `Total solutions: 3`
**Expected:** `Status: OPTIMAL`

Needs `CMAKE_PREFIX_PATH` pointing at the OR-Tools folder; see the skill's Install section.

Enumeration reports one solution per assignment of *every* variable in the model. The model here has only the six decision variables, so each subset appears once. If you add an auxiliary variable that is not fixed by the decision variables, each subset is reported once per value of that auxiliary variable: the model with `aux` bounded by `x + y <= aux` reports 18 solutions for a 6-solution problem. Either leave auxiliary variables out of the enumerated model or count distinct decision values.
