# Traffic lights: a junction has four vehicle lights and four pedestrian lights; the
# light states of neighbouring roads must form one of the safe combinations, going
# round the junction (road 4 is followed by road 1).
import cpmpy as cp


def build(instance):
    # Safe combinations of (vehicle light i, pedestrian light i, vehicle light i+1, pedestrian light i+1).
    allowed_tuples = instance["allowed_tuples"]

    # State ranges fixed by the problem (not by the instance):
    # vehicle lights 0=red, 1=red-yellow, 2=green, 3=yellow; pedestrian lights 0=red, 1=green.
    vehicle = cp.intvar(0, 3, shape=4, name="vehicle")
    pedestrian = cp.intvar(0, 1, shape=4, name="pedestrian")

    model = cp.Model()

    # For every road i, its own lights together with those of the next road (wrapping
    # from road 4 back to road 1) must be one of the safe combinations.
    for i in range(4):
        nxt = (i + 1) % 4
        model += cp.Table([vehicle[i], pedestrian[i], vehicle[nxt], pedestrian[nxt]], allowed_tuples)

    # Output order is [V1, V2, V3, V4, P1, P2, P3, P4].
    lights = list(vehicle) + list(pedestrian)

    return model, {"lights": lights}
