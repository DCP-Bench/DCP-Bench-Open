# Traffic junction: eight traffic lights, four vehicle lights V1..V4 and four
# pedestrian lights P1..P4. Find a light state for each light such that every
# consecutive pair of junction states (V_i, P_i, V_i+1, P_i+1), cyclic, is safe.
from paramita.modelling import Bool, And, If

VEHICLE_STATES = 4  # 0 red, 1 red-yellow, 2 green, 3 yellow (problem constant)
PEDESTRIAN_STATES = 2  # 0 red, 1 green (problem constant)


def build(instance):
    tuples = instance["allowed_tuples"]
    k = 4  # the junction has four vehicle and four pedestrian lights (problem constant)

    # one-hot state of every light
    V = {i: [Bool(f"V_{i}_{s}") for s in range(VEHICLE_STATES)] for i in range(k)}
    P = {i: [Bool(f"P_{i}_{s}") for s in range(PEDESTRIAN_STATES)] for i in range(k)}
    cons = [sum(V[i]) == 1 for i in range(k)] + [sum(P[i]) == 1 for i in range(k)]

    # every pair (V_i, P_i, V_i+1, P_i+1), with light 5 being light 1, is an allowed tuple
    for i in range(k):
        j = (i + 1) % k
        choice = [Bool(f"pair_{i}_{t}") for t in range(len(tuples))]
        cons.append(sum(choice) == 1)
        for t, (v1, p1, v2, p2) in enumerate(tuples):
            cons.append(If(choice[t], And([V[i][v1], P[i][p1], V[j][v2], P[j][p2]])))

    # output: the lights in the order V1..V4, P1..P4, each as its state number
    lights = [sum(s * V[i][s] for s in range(VEHICLE_STATES)) for i in range(k)]
    lights += [sum(s * P[i][s] for s in range(PEDESTRIAN_STATES)) for i in range(k)]
    return cons, {"lights": lights}
