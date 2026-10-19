# One machine with release times (scheduling)

**Problem:** run four tasks on one machine, each after its release time, with `cut` before `paint`, minimising the finish time of the last task.
**Shows:** start-time integers with lower bounds, no-overlap by an order binary per pair with two `add_indicator` constraints (no big-M), precedence, minimise a makespan variable, `mipgap = 0`, the result accepted only on `integer optimal solution`.
**Run:** `python3 model.py`
**Expected:** `Makespan: 11 (integer optimal solution)`
**Expected:** `cut    starts  0 ends  3`
