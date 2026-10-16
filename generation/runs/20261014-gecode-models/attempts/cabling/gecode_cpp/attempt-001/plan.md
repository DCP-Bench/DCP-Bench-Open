# Plan: cabling (attempt-001)

Rack of n devices, each in its own 1U slot; find the slot order that minimises the sum of cable lengths.

- each device takes a different slot -> `distinct(*this, pos, IPL_DOM)` (pos[d] = slot of device d, slots 0..n-1)
- cable length between two devices = number of U between their slots -> `abs(pos[a] - pos[b])` as `expr(*this, abs(pos[a] - pos[b]), IPL_DOM)`
- a cable count multiplies its length (several cables between the same pair) -> weighted `sum(IntArgs(counts), lengths)`, one term per cable line of the instance
- total sum of all cable lengths -> `IntVar total = expr(*this, sum(IntArgs(counts), lengths))`, output `final_sum`
- branching: slots of devices in order, first fail on the slot domain, smallest slot first -> `branch(*this, pos, INT_VAR_SIZE_MIN(), INT_VAL_MIN())`
- objective: minimise the total -> `minimize(total)`
