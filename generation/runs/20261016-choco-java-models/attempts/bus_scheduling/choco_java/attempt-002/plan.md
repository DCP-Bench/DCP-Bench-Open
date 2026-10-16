# Plan: minimum buses on a cyclic day of 4-hour slots (bus_scheduling)

- "the demand for buses in each 4-hour interval" -> demands[i] (instance field, 6 slots)
- "each bus operates 8 successive hours, so two slots" -> x[i] = buses starting in slot i, each covers slots i and i+1
- "buses on duty in slot i meet the demand" -> x[i] + x[i-1] >= demands[i], with i-1 wrapping from slot 0 to slot 5 (the day repeats)
- "minimum number of buses" -> minimise sum of x
- "print the number of buses scheduled in each time slot (x)" -> output x
