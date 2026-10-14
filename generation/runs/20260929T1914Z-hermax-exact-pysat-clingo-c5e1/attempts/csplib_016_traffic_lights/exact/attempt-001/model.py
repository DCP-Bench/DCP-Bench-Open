# Traffic lights: a four-way junction has four vehicle lights V1..V4 and four
# pedestrian lights P1..P4. Pick a state for each so that every pair of
# neighbouring roads shows one of the safe combinations.
from exact import Exact


def build(instance):
    # safe combinations of (V_i, P_i, V_{i+1}, P_{i+1}); everything else is forbidden
    allowed_tuples = instance["allowed_tuples"]

    solver = Exact()
    # vehicle lights: 0 = red, 1 = red-yellow, 2 = green, 3 = yellow
    vehicle = [f"V{i + 1}" for i in range(4)]
    for name in vehicle:
        solver.addVariable(name, 0, 3)
    # pedestrian lights: 0 = red, 1 = green
    pedestrian = [f"P{i + 1}" for i in range(4)]
    for name in pedestrian:
        solver.addVariable(name, 0, 1)

    # each road and the next one (road 4 is followed by road 1) must show a safe
    # combination: exactly one allowed tuple is selected, and the four lights take
    # that tuple's values
    for i in range(4):
        nxt = (i + 1) % 4
        lights = [vehicle[i], pedestrian[i], vehicle[nxt], pedestrian[nxt]]
        selected = [f"road{i}_uses_tuple{k}" for k in range(len(allowed_tuples))]
        for name in selected:
            solver.addVariable(name, 0, 1)
        solver.addConstraint([(1, name) for name in selected], True, 1, True, 1)
        for position, light in enumerate(lights):
            solver.addConstraint([(1, light)] + [(-allowed_tuples[k][position], selected[k])
                                                 for k in range(len(allowed_tuples))
                                                 if allowed_tuples[k][position] != 0],
                                 True, 0, True, 0)

    # reported in the order V1, V2, V3, V4, P1, P2, P3, P4
    return solver, {"lights": vehicle + pedestrian}
