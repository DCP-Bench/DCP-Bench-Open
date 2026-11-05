#!/usr/bin/python3
# Category: cpmpy_examples
# Source: https://github.com/CPMpy/cpmpy/blob/master/examples/wolf_goat_cabbage.py
# Description: https://en.wikipedia.org/wiki/Wolf,_goat_and_cabbage_problem

# Data
stage = 8  # Number of stages
# End of data

# Import libraries
from cpmpy import *
import json

wolf_pos = boolvar(stage)
cabbage_pos = boolvar(stage)
goat_pos = boolvar(stage)
boat_pos = boolvar(stage)

model = Model(
    # Initial situation
    (boat_pos[0] == 0),
    (wolf_pos[0] == 0),
    (goat_pos[0] == 0),
    (cabbage_pos[0] == 0),

    # Boat keeps moving between shores
    [boat_pos[i] != boat_pos[i - 1] for i in range(1, stage)],

    # Final situation
    (boat_pos[-1] == 1),
    (wolf_pos[-1] == 1),
    (goat_pos[-1] == 1),
    (cabbage_pos[-1] == 1),

    # # Wolf and goat cannot be left alone
    [(goat_pos[i] != wolf_pos[i]) | (boat_pos[i] == wolf_pos[i]) for i in range(stage)],

    # # Goat and cabbage cannot be left alone
    [(goat_pos[i] != cabbage_pos[i]) | (boat_pos[i] == goat_pos[i]) for i in range(stage)],

    # # Only one animal/cabbage can move per turn
    [abs(wolf_pos[i] - wolf_pos[i + 1]) + abs(goat_pos[i] - goat_pos[i + 1]) + abs(
        cabbage_pos[i] - cabbage_pos[i + 1]) <= 1 for i in range(stage - 1)],
)

# Solve
model.solve()

# Print
solution = {"wolf_pos": wolf_pos.value().tolist(), "goat_pos": goat_pos.value().tolist(),
            "cabbage_pos": cabbage_pos.value().tolist(), "boat_pos": boat_pos.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script
