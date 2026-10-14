from pycsp3 import *

# Wolf, goat and cabbage: the farmer starts with all four on the starting shore (0) and
# must bring all four to the destination shore (1). The boat carries the farmer and at
# most one item. The stages are the states of the river crossing, one stage per crossing.

stage = data.stage

# wolf_pos[t] is 1 when the wolf is on the destination shore at stage t
wolf_pos = VarArray(size=stage, dom={0, 1})
# goat_pos[t] is 1 when the goat is on the destination shore at stage t
goat_pos = VarArray(size=stage, dom={0, 1})
# cabbage_pos[t] is 1 when the cabbage is on the destination shore at stage t
cabbage_pos = VarArray(size=stage, dom={0, 1})
# boat_pos[t] is 1 when the boat is on the destination shore at stage t
boat_pos = VarArray(size=stage, dom={0, 1})

satisfy(
    # at the start, everything is on the starting shore
    wolf_pos[0] == 0,
    goat_pos[0] == 0,
    cabbage_pos[0] == 0,
    boat_pos[0] == 0,

    # at the end, everything is on the destination shore
    wolf_pos[stage - 1] == 1,
    goat_pos[stage - 1] == 1,
    cabbage_pos[stage - 1] == 1,
    boat_pos[stage - 1] == 1,

    # the farmer rows the boat from one shore to the other at every crossing
    [boat_pos[t] != boat_pos[t + 1] for t in range(stage - 1)],

    # the boat carries at most one item besides the farmer
    [Sum(wolf_pos[t] != wolf_pos[t + 1], goat_pos[t] != goat_pos[t + 1],
         cabbage_pos[t] != cabbage_pos[t + 1]) <= 1 for t in range(stage - 1)],

    # an item that crosses the river is carried by the boat
    [imply(wolf_pos[t] != wolf_pos[t + 1], boat_pos[t] == wolf_pos[t]) for t in range(stage - 1)],
    [imply(goat_pos[t] != goat_pos[t + 1], boat_pos[t] == goat_pos[t]) for t in range(stage - 1)],
    [imply(cabbage_pos[t] != cabbage_pos[t + 1], boat_pos[t] == cabbage_pos[t]) for t in range(stage - 1)],

    # the wolf is never left alone with the goat, unless the farmer is there
    [imply(wolf_pos[t] == goat_pos[t], boat_pos[t] == wolf_pos[t]) for t in range(stage)],

    # the goat is never left alone with the cabbage, unless the farmer is there
    [imply(goat_pos[t] == cabbage_pos[t], boat_pos[t] == goat_pos[t]) for t in range(stage)],
)
