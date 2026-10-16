from pycsp3 import *

# Eight traffic lights at a four-way junction: V1 to V4 are the vehicle lights,
# P1 to P4 the pedestrian lights. Every combination (V_i, P_i, V_{i+1}, P_{i+1})
# must be one of the safe combinations, for i = 1..4 with V_5 = V_1 and P_5 = P_1.

safe = data.allowed_tuples

# lights = [V1, V2, V3, V4, P1, P2, P3, P4]
lights = VarArray(size=8, dom=range(4))

satisfy(
    # the pedestrian lights are red (0) or green (1)
    [lights[4 + k] <= 1 for k in range(4)],

    # each pair of neighbouring junction lights must be a safe combination
    [Table(scope=[lights[i], lights[4 + i], lights[(i + 1) % 4], lights[4 + (i + 1) % 4]],
           supports=safe) for i in range(4)],
)
