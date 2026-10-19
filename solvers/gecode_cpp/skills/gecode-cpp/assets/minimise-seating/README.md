# Row seating (minimise)

**Problem:** seat 6 guests in a row of 6 chairs, no two enemies side by side, minimising the total distance from each guest's preferred chair.
**Shows:** `IntMinimizeSpace`, `channel` between a permutation and its inverse with `IPL_DOM`, `abs` in MiniModel, an objective built with `expr(*this, sum(...))`, `BAB`.
**Run:** `g++ -std=c++17 -O2 model.cpp -o model -lgecodesearch -lgecodeminimodel -lgecodeset -lgecodefloat -lgecodeint -lgecodekernel -lgecodesupport && ./model`
**Expected:** `Total distance: 8`

The optimum 8 was checked against all 720 permutations in Python.
