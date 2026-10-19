# csplib_016_traffic_lights: a four-way traffic junction with eight traffic lights.
# Four vehicle lights V1..V4 take states 0=red, 1=red-yellow, 2=green, 3=yellow.
# Four pedestrian lights P1..P4 take states 0=red, 1=green.
# The instance lists the safe combinations (V_i, P_i, V_{i+1}, P_{i+1}), i=1..4,
# with V_5=V_1 and P_5=P_1. Every other combination is disallowed.
# Output: lights = [V1, V2, V3, V4, P1, P2, P3, P4].
import mip


def build(instance):
    allowed = instance["allowed_tuples"]
    k_count = len(allowed)

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # Light variables: vehicle lights take states 0..3, pedestrian lights 0..1.
    V = [model.add_var(f"V{i + 1}", lb=0, ub=3, var_type=mip.INTEGER) for i in range(4)]
    P = [model.add_var(f"P{i + 1}", lb=0, ub=1, var_type=mip.INTEGER) for i in range(4)]

    # Safe combinations: for each i=1..4 (indices 0..3, with the wrap from 4 back to 1),
    # the tuple (V_i, P_i, V_{i+1}, P_{i+1}) must be one of the allowed tuples.
    # Every other combination is disallowed, so one binary per allowed tuple picks
    # exactly one of them, and the four lights are tied to the chosen tuple.
    for i in range(4):
        j = (i + 1) % 4
        z = [model.add_var(f"z_{i}_{k}", var_type=mip.BINARY) for k in range(k_count)]
        model += mip.xsum(z) == 1
        model += V[i] == mip.xsum(allowed[k][0] * z[k] for k in range(k_count))
        model += P[i] == mip.xsum(allowed[k][1] * z[k] for k in range(k_count))
        model += V[j] == mip.xsum(allowed[k][2] * z[k] for k in range(k_count))
        model += P[j] == mip.xsum(allowed[k][3] * z[k] for k in range(k_count))

    # No objective: the problem is satisfaction, so any valid assignment answers it.
    return model, {"lights": V + P}
