"""Traffic lights: four crossings in a ring, each with a vehicle light V_i (r, ry, g, y as
0..3) and a pedestrian light P_i (r, g as 0..1). Neighbouring crossings i and i+1 (with
crossing 5 being crossing 1) must show one of the allowed combinations (V_i, P_i, V_i+1, P_i+1).

The model reports the lights as [V1, V2, V3, V4, P1, P2, P3, P4].
"""
from docplex.mp.model import Model


def build(instance):
    allowed = instance["allowed_tuples"]  # allowed (V_i, P_i, V_i+1, P_i+1) combinations
    crossings = 4  # the problem has four crossings in a ring

    model = Model("traffic_lights")

    # Vehicle lights take the states r, ry, g, y (0..3); pedestrian lights r, g (0..1).
    vehicle = [model.integer_var(0, 3, name=f"V{i + 1}") for i in range(crossings)]
    pedestrian = [model.integer_var(0, 1, name=f"P{i + 1}") for i in range(crossings)]

    # A combination with a state outside these ranges can never be shown.
    usable = [t for t in allowed if 0 <= t[0] <= 3 and 0 <= t[1] <= 1 and 0 <= t[2] <= 3 and 0 <= t[3] <= 1]

    # Every pair of neighbouring crossings shows one allowed combination. shows[i][t] is 1 when
    # crossings i and i+1 show combination t; exactly one is shown, and the four lights read it.
    for i in range(crossings):
        nxt = (i + 1) % crossings
        shows = [model.binary_var(name=f"shows_{i}_{t}") for t in range(len(usable))]
        model.add_constraint(model.sum(shows) == 1)
        model.add_constraint(vehicle[i] == model.sum(usable[t][0] * shows[t] for t in range(len(usable))))
        model.add_constraint(pedestrian[i] == model.sum(usable[t][1] * shows[t] for t in range(len(usable))))
        model.add_constraint(vehicle[nxt] == model.sum(usable[t][2] * shows[t] for t in range(len(usable))))
        model.add_constraint(pedestrian[nxt] == model.sum(usable[t][3] * shows[t] for t in range(len(usable))))

    return model, {"lights": vehicle + pedestrian}
