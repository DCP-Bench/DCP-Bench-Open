A number of cars are to be produced; cars are not identical -> one slot variable per car in the sequence, value = car type (class), N = sum of demand -> IntVarArray x(*this, N, 0, C-1); count(*this, x, c, IRT_EQ, demand[c]) per class (demand of each type met exactly, ordered by hardness)
different variants are available as options on the basic model -> one Boolean per (option, slot) b[o][i] = requires[type(x_i)][o] -> element(*this, IntArgs(col_o), x[i], b[o][i]) per option and slot
stations install the options and handle at most a certain percentage of the cars -> per option: at most at_most[o] of every per_slots[o] consecutive cars need it -> sequence(*this, b[o], IntSet(1,1), per_slots[o], 0, at_most[o], IPL_DOM)
cars requiring an option must not be bunched together -> same sequence constraint (window of per_slots[o] cars) as above
implied: the first t slots hold at most a*(t/q)+min(a,t%q) requiring cars, and at least D_o minus the bound for the remaining N-t slots -> linear(*this, prefix_o(t), IRT_LQ / IRT_GQ, bound) for every t, which lets the search prune prefixes early (the skill's Search section, implied prefix bounds)
print the sequence of car types (0-based, original numbering) -> y[i] = element(IntArgs(order), x[i]) to map the internal value back to the car type; output y
branching -> branch slots in order (INT_VAR_NONE) and try the hardest value first (INT_VAL_MIN) over the internal values, where internal value 0 is the most constrained class (sum over its options of at_most/per_slots, descending)
objective -> none (satisfaction)
