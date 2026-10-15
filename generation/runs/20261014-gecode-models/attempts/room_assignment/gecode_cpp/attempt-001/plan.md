Each request is assigned to one room from 0 to max_rooms - 1 -> IntVarArray room(*this, n, 0, max_rooms - 1)
Some requests already have a room pre-assigned -> rel(*this, room[i], IRT_EQ, p) for each p >= 0
A room can only serve one request at a time: requests that overlap in time must get different rooms. Overlap is taken per start day, the requests active on a day (start <= day < end) form a clique -> distinct(*this, active, room, IPL_DOM) for each distinct start day with two or more active requests; a clique covers every overlapping pair since each overlapping pair is active together on the later start day (interval graph, cliques suffice, fewer posts than pairs)
Dates are YYYY-MM-DD strings; they are converted to day numbers in the constructor (end date exclusive, as the back_to_back instance note states) -> days_from_civil helper, no constraint
Branching -> branch(*this, room, INT_VAR_SIZE_MIN(), INT_VAL_MIN())
Objective -> none (satisfaction); output room_assignments only
