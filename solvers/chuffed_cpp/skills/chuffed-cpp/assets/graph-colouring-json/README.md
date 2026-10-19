# Graph colouring from a JSON file (minimise)

**Problem:** colour the nodes of a graph so that neighbours differ, with as few colours as possible; the graph is a ragged list of neighbour lists in `data.json`.
**Shows:** reading data with nlohmann/json from the path in `argv[1]` (default `data.json`), every size taken from the data, a ragged `std::vector<std::vector<int>>`, ignored extra keys (`note`), linking `nlohmann_json::nlohmann_json` in CMake, `int_rel(x, IRT_NE, y)`, `maximum`, fixing one node's colour against interchangeable colours, `optimize(top, OPT_MIN)`.
**Run:** `cmake -S . -B build -DCMAKE_BUILD_TYPE=Release && cmake --build build && ./build/model data.json`
**Expected:** `graph five-cycle-plus-hub, 6 nodes`
**Expected:** `Minimum colours: 3`

Install the JSON library with `apt install nlohmann-json3-dev` (Debian/Ubuntu) or `brew install nlohmann-json`; it is header only, so copying `json.hpp` next to the program also works.
