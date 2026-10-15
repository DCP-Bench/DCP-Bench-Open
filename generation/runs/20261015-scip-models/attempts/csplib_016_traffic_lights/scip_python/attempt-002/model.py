# Traffic lights: set the states of 4 vehicle lights V1..V4 and 4 pedestrian lights P1..P4 so
# that every consecutive pair (V_i, P_i, V_{i+1}, P_{i+1}), with V_5 = V_1 and P_5 = P_1,
# is one of the safe combinations listed in the instance.
from pyscipopt import Model, quicksum


def build(instance):
    allowed = instance["allowed_tuples"]
    tuples = [tuple(t) for t in allowed]
    K = len(tuples)
    n_lights = 4
    m = Model()

    # vehicle states: 0=red, 1=red-yellow, 2=green, 3=yellow (from the problem statement)
    V = [m.addVar(name=f"V_{i}", vtype="I", lb=0, ub=3) for i in range(n_lights)]
    # pedestrian states: 0=red, 1=green (from the problem statement)
    P = [m.addVar(name=f"P_{i}", vtype="I", lb=0, ub=1) for i in range(n_lights)]

    # selector b[i, k] = 1 if the pair (V_i, P_i, V_{i+1}, P_{i+1}) equals the k-th allowed tuple
    b = {(i, k): m.addVar(name=f"b_{i}_{k}", vtype="B") for i in range(n_lights) for k in range(K)}

    for i in range(n_lights):
        j = (i + 1) % n_lights  # wrap: V_5 = V_1, P_5 = P_1
        # each consecutive pair must match exactly one allowed combination
        m.addCons(quicksum(b[i, k] for k in range(K)) == 1, name=f"one_tuple_{i}")
        # the pair (V_i, P_i, V_{i+1}, P_{i+1}) is the chosen allowed combination
        m.addCons(V[i] == quicksum(tuples[k][0] * b[i, k] for k in range(K)), name=f"V_i_{i}")
        m.addCons(P[i] == quicksum(tuples[k][1] * b[i, k] for k in range(K)), name=f"P_i_{i}")
        m.addCons(V[j] == quicksum(tuples[k][2] * b[i, k] for k in range(K)), name=f"V_next_{i}")
        m.addCons(P[j] == quicksum(tuples[k][3] * b[i, k] for k in range(K)), name=f"P_next_{i}")

    # the output lists the lights as [V1, V2, V3, V4, P1, P2, P3, P4]
    lights = V + P
    return m, {"lights": lights}
