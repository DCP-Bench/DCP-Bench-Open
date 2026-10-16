# Data from a JSON file (knapsack)

**Problem:** the knapsack of `maximise-knapsack` read from `data.json` (path as first argument).
**Shows:** reading sizes and values from JSON with nlohmann/json (`apt install nlohmann-json3-dev`), no sizes written into the model.
**Run:** `g++ -std=c++17 -O2 model.cpp -o model -I"$HIGHS_PREFIX/include/highs" -L"$HIGHS_PREFIX/lib" -lhighs -lpthread && ./model`
**Expected:** `Value: 15 with 4 items`
