# Pigeonhole (infeasible)

**Problem:** place 4 pigeons into 3 holes with no two pigeons in the same hole.
**Shows:** `AddAllDifferent` over more values than the domain offers, and that infeasibility is reported through the status, not as an error or an empty result.
**Run:** `cmake -S . -B build && cmake --build build && ./build/model`
**Expected:** `Status: INFEASIBLE`
**Expected:** `No placement exists`

Needs `CMAKE_PREFIX_PATH` pointing at the OR-Tools folder; see the skill's Install section.
