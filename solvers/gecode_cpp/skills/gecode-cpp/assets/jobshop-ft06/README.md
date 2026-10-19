# Job shop, ft06 (scheduling, minimise the makespan)

**Problem:** 6 jobs, each a fixed sequence of 6 operations on 6 machines (Fisher and Thompson's ft06); every machine runs one operation at a time; minimise the time the last operation ends.
**Shows:** precedence chains inside each job (`rel` on start plus duration), one `unary` per machine built from the tasks on it, the makespan as `max` over the task ends, `BAB` on an `IntMinimizeSpace` with `cost()`, start-time branching (`INT_VAR_MIN_MIN`).
**Run:** `g++ -std=c++17 -O2 model.cpp -o model -lgecodesearch -lgecodeminimodel -lgecodeset -lgecodefloat -lgecodeint -lgecodekernel -lgecodesupport && ./model`
**Expected:** `Makespan: 55`

55 is the published optimum of ft06. The same pattern covers any job shop: the data is the list of (machine, duration) pairs in processing order.
