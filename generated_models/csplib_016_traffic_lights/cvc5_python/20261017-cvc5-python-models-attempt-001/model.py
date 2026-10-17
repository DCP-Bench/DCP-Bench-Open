# Traffic lights (csplib 016): a four-way junction with 4 vehicle lights V1..V4 and 4 pedestrian lights P1..P4.
import cvc5.pythonic as cz


def build(instance):
    allowed = instance["allowed_tuples"]  # safe (V_i, P_i, V_next, P_next) combinations from the data
    n = 4  # the junction has four roads, and the cycle wraps from light 4 back to light 1

    # Vehicle light states: 0=red, 1=red-yellow, 2=green, 3=yellow. Pedestrian light states: 0=red, 1=green.
    V = [cz.Int(f"V{i + 1}") for i in range(n)]
    P = [cz.Int(f"P{i + 1}") for i in range(n)]

    # the vehicle light states are 0 to 3 and the pedestrian light states are 0 to 1
    domains = []
    for i in range(n):
        domains += [V[i] >= 0, V[i] <= 3, P[i] >= 0, P[i] <= 1]

    # the combinations (V_i, P_i, V_i+1, P_i+1) of light states must be safe for intersecting roads, i = 1..4 with V_5 = V_1 and P_5 = P_1; every other combination is disallowed
    table = []
    for i in range(n):
        j = (i + 1) % n
        table.append(
            cz.Or([
                cz.And(V[i] == a, P[i] == b, V[j] == c, P[j] == d)
                for a, b, c, d in allowed
            ])
        )

    constraints = domains + table
    lights = V + P  # output order: V1, V2, V3, V4, P1, P2, P3, P4
    return constraints, {"lights": lights}
