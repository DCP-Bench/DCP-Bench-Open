# Worker-to-task assignment (minimise)

**Problem:** assign 4 workers to 4 different tasks at minimum total cost from a cost table.
**Shows:** `AddElement` with a constant array indexed by a variable, `AddAllDifferent`, `Minimize`, status check, reading the chosen task of each worker.
**Run:** `cmake -S . -B build && cmake --build build && ./build/model`
**Expected:** `Status: OPTIMAL`
**Expected:** `Minimum cost: 13`

Needs `CMAKE_PREFIX_PATH` pointing at the OR-Tools folder; see the skill's Install section. The element constraint takes the constant table as `absl::Span<const int64_t>`; a table of variables needs a `std::vector<LinearExpr>` instead.
