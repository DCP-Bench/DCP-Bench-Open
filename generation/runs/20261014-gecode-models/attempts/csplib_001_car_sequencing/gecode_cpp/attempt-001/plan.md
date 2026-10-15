# Plan: csplib_001_car_sequencing (attempt-001)

Variables: the sequence of car types, one slot per car, value 0..types-1; n = total demand.
- A car type appears as many times as its demand -> count(*this, seq, t, IRT_EQ, demand[t]) for every type t.
- Each option o: in any window of per_slots[o] consecutive cars, at most at_most[o] cars require it -> sequence(*this, seq, IntSet(S_o), per_slots[o], 0, at_most[o]) with S_o = {t : requires[t][o] = 1}.
- Branching: seq with INT_VAR_AFC_SIZE_MAX(0.99) and INT_VAL_MIN, with Luby restarts (restarts(100)): learns which positions fail on the 200-car instances.
- Objective: none (satisfaction). Output: sequence.
