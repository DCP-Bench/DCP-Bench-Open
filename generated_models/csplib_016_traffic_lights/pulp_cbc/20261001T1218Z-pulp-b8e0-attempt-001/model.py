"""Traffic lights: a four-way junction has four vehicle lights V1..V4 and four pedestrian
lights P1..P4. For each i = 1..4 the combination (V_i, P_i, V_{i+1}, P_{i+1}), with
V_5 = V_1 and P_5 = P_1, must be one of the allowed tuples.

The model reports the eight light states in the order [V1..V4, P1..P4].
"""
import pulp


def build(instance):
    allowed = instance["allowed_tuples"]  # each row is (V_i, P_i, V_{i+1}, P_{i+1})

    problem = pulp.LpProblem("traffic_lights", pulp.LpMinimize)  # satisfaction: no objective

    # Light states. Problem constants: a vehicle light is 0 red, 1 red-yellow, 2 green,
    # 3 yellow; a pedestrian light is 0 red, 1 green.
    vehicle = [pulp.LpVariable(f"V{i + 1}", 0, 3, cat="Integer") for i in range(4)]
    pedestrian = [pulp.LpVariable(f"P{i + 1}", 0, 1, cat="Integer") for i in range(4)]

    # Table constraint for every pair of neighbouring roads (road 4 is followed by road 1):
    # pick[i][k] = 1 if the combination at junction corner i is the k-th allowed tuple.
    # Exactly one tuple is picked, and the four lights concerned take that tuple's values.
    pick = pulp.LpVariable.dicts("pick", (range(4), range(len(allowed))), cat="Binary")
    for i in range(4):
        j = (i + 1) % 4
        corner = [vehicle[i], pedestrian[i], vehicle[j], pedestrian[j]]
        problem += pulp.lpSum(pick[i][k] for k in range(len(allowed))) == 1
        for position in range(4):
            problem += corner[position] == pulp.lpSum(
                allowed[k][position] * pick[i][k] for k in range(len(allowed)))

    return problem, {"lights": vehicle + pedestrian}
