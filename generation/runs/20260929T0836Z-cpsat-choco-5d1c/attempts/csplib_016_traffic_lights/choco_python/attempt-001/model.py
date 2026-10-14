# Traffic lights: a four-way junction has four vehicle lights V1..V4 and four
# pedestrian lights P1..P4. Pick a state for each so that every pair of
# neighbouring roads shows one of the safe combinations.
from pychoco.model import Model


def build(instance):
    # safe combinations of (V_i, P_i, V_{i+1}, P_{i+1}); everything else is forbidden
    allowed_tuples = instance["allowed_tuples"]

    model = Model()

    # vehicle lights: 0 = red, 1 = red-yellow, 2 = green, 3 = yellow
    vehicle = [model.intvar(0, 3, name=f"V{i + 1}") for i in range(4)]
    # pedestrian lights: 0 = red, 1 = green
    pedestrian = [model.intvar(0, 1, name=f"P{i + 1}") for i in range(4)]

    # each road and the next one (road 4 is followed by road 1) must show a safe combination
    for i in range(4):
        nxt = (i + 1) % 4
        model.table([vehicle[i], pedestrian[i], vehicle[nxt], pedestrian[nxt]], allowed_tuples).post()

    # reported in the order V1, V2, V3, V4, P1, P2, P3, P4
    return model, {"lights": vehicle + pedestrian}
