# SEND + MORE = MONEY (satisfy)

**Problem:** give each letter a different digit so that SEND + MORE = MONEY, with no leading zero.
**Shows:** a `Space` subclass, `distinct` with `IPL_DOM`, a linear MiniModel equation, `DFS` for the first solution, telling "no solution" from "stopped" with `engine.stopped()`.
**Run:** `g++ -std=c++17 -O2 model.cpp -o model -lgecodesearch -lgecodeminimodel -lgecodeset -lgecodefloat -lgecodeint -lgecodekernel -lgecodesupport && ./model`
**Expected:** `9567 + 1085 = 10652`

Shortened from Gecode's own `examples/money.cpp`.
