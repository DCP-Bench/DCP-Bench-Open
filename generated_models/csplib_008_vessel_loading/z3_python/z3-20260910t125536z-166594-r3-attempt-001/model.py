import z3


def build(instance):
    deck_width = instance["deck_width"]
    deck_length = instance["deck_length"]
    count = instance["n_containers"]
    width = instance["width"]
    length = instance["length"]
    classes = instance["classes"]
    separation = instance["separation"]

    left = [z3.Int(f"left_{i}") for i in range(count)]
    right = [z3.Int(f"right_{i}") for i in range(count)]
    top = [z3.Int(f"top_{i}") for i in range(count)]
    bottom = [z3.Int(f"bottom_{i}") for i in range(count)]

    constraints = []
    for i in range(count):
        constraints.append(z3.And(left[i] >= 0, left[i] <= deck_width))
        constraints.append(z3.And(right[i] >= 0, right[i] <= deck_width))
        constraints.append(z3.And(top[i] >= 0, top[i] <= deck_length))
        constraints.append(z3.And(bottom[i] >= 0, bottom[i] <= deck_length))
        # Each container sits in one of its two orientations.
        constraints.append(z3.Or(
            z3.And(right[i] - left[i] == width[i], top[i] - bottom[i] == length[i]),
            z3.And(right[i] - left[i] == length[i], top[i] - bottom[i] == width[i])))

    for x in range(count):
        for y in range(x + 1, count):
            gap = separation[classes[x] - 1][classes[y] - 1]
            # Separated in at least one of the four directions.
            constraints.append(z3.Or(right[x] + gap <= left[y],
                                     left[x] >= right[y] + gap,
                                     top[x] + gap <= bottom[y],
                                     bottom[x] >= top[y] + gap))

    return constraints, {"left": left, "right": right, "top": top, "bottom": bottom}
