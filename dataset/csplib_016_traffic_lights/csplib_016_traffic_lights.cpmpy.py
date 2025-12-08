#!/usr/bin/python3
# Category: csplib
# Source description: https://www.csplib.org/Problems/prob016/

"""
Imagine a four-way traffic junction with eight traffic lights. Four lights (V1 to V4) are for vehicles, and four (P1 to P4)
are for pedestrians. The lights have different states (e.g., red, green). The problem parameters describe constraints on which
combinations of light states are safe. Specifically, certain combinations of vehicle and pedestrian light states for
intersecting roads are disallowed to prevent accidents: (V_i, P_i, V_{i+1}, P_{i+1}) for i=1..4 (with V_5=V_1 and P_5=P_1).

Vehicle light states: 0=red, 1=red-yellow, 2=green, 3=yellow
Pedestrian light states: 0=red, 1=green

Print a valid 8-tuple of light states (lights) as a list of integers with the order [V1, V2, V3, V4, P1, P2, P3, P4].
"""

# Data
# Allowed combinations for (V_i, P_i, V_{i+1}, P_{i+1}) for i=1..4 (with V_5=V_1 and P_5=P_1)
# where V_i is the vehicle light state and P_i is the pedestrian light state.
# (r, r, g, g) -> (0, 0, 2, 1)
# (ry, r, y, r) -> (1, 0, 3, 0)
# (g, g, r, r) -> (2, 1, 0, 0)
# (y, r, ry, r) -> (3, 0, 1, 0)
# These combinations ensure that intersecting roads do not have green lights simultaneously.
allowed_tuples = [[0, 0, 2, 1], [1, 0, 3, 0], [2, 1, 0, 0], [3, 0, 1, 0]]
# End of data

# Import libraries
from cpmpy import *
import json

# Decision Variables
V1 = intvar(0, 3, name="V1")
V2 = intvar(0, 3, name="V2")
V3 = intvar(0, 3, name="V3")
V4 = intvar(0, 3, name="V4")
P1 = intvar(0, 1, name="P1")
P2 = intvar(0, 1, name="P2")
P3 = intvar(0, 1, name="P3")
P4 = intvar(0, 1, name="P4")

vehicle_lights = [V1, V2, V3, V4]
pedestrian_lights = [P1, P2, P3, P4]

lights = cpm_array([V1, V2, V3, V4, P1, P2, P3, P4])

# Model
model = Model()

# Quaternary constraints on intersecting roads
for i in range(4):
    model += Table([vehicle_lights[i], pedestrian_lights[i],
                    vehicle_lights[(i + 1) % 4], pedestrian_lights[(i + 1) % 4]],
                   allowed_tuples)

# Solve
model.solve()

# Print
solution = {"lights": lights.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script