Stages 0..n-1 (n = instance stage, even). Position 0 = starting shore, 1 = destination.
Start: all on shore 0 at stage 0. End: all on shore 1 at last stage.
A farmer with a wolf, a goat and a cabbage must cross by boat; the boat carries the farmer and at most one item.
- the farmer crosses the river at every stage, boat alternates -> boat[t] != boat[t+1] (boat[0] = 0, boat[n-1] = 1 forces n even) -> rel(*this, boat[t] != boat[t+1]) (IntVar, domain 0..1; integer outputs, since BoolVarArray outputs crash the driver)
- the boat carries only the farmer and a single item: at most one item changes shore per stage -> flip_x = (x[t] XOR x[t+1]) for each item, linear(flips, IRT_LQ, 1)
- an item can only be carried if it is on the farmer's shore -> flip_x -> x[t] == boat[t] (half-reified rel with imp)
- the wolf would eat the goat if left unattended: wolf and goat on the same shore without the farmer is forbidden -> ws <=> (wolf == goat), ws -> wolf == boat
- the goat would eat the cabbage if left unattended: goat and cabbage on the same shore without the farmer is forbidden -> gc <=> (goat == cabbage), gc -> goat == boat
- branching: wolf, goat, cabbage, then boat, all in stage order (INT_VAR_NONE, value min); the flips are decided by the positions.
- objective: none (satisfaction).
