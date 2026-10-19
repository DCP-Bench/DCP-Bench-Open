# Shift roster from a JSON file (JSON input, minimise)

**Problem:** assign 4 workers an off / day / night shift on each of 7 days, meeting each day's demand, no day shift right after a night, at most two nights in a row, at most `max_nights` nights each, nobody on their days off; minimise the total cost.
**Shows:** reading `argv[1]` (default `data.json`) with header-only [nlohmann/json](https://json.nlohmann.me/) (Debian/Ubuntu `nlohmann-json3-dev`), every size from the data, a ragged list (`days_off`), unused keys (`name`, `note`) ignored; `Matrix`, gcc as `count` with cardinality sets, a `REG`/`DFA` shift rule with `extensional`, `element` over a cost table, AFC branching, `BAB`.
**Run:** `g++ -std=c++17 -O2 model.cpp -o model -lgecodesearch -lgecodeminimodel -lgecodeset -lgecodefloat -lgecodeint -lgecodekernel -lgecodesupport && ./model data.json`
**Expected:** `Total cost: 36`

Proven optimal in about 0.1 s on Gecode 6.2.0 (0.07 s measured).
