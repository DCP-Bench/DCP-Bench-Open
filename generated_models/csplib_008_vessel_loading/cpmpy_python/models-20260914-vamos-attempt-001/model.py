import itertools

import cpmpy as cp


def build(instance):
    deck_width = instance["deck_width"]
    deck_length = instance["deck_length"]
    n = instance["n_containers"]
    width, length = instance["width"], instance["length"]
    classes, separation = instance["classes"], instance["separation"]

    left = cp.intvar(0, deck_width, shape=n, name="left")
    right = cp.intvar(0, deck_width, shape=n, name="right")
    top = cp.intvar(0, deck_length, shape=n, name="top")
    bottom = cp.intvar(0, deck_length, shape=n, name="bottom")

    model = cp.Model()
    for i in range(n):
        # Either orientation of the container.
        model += (((right[i] - left[i] == width[i]) & (top[i] - bottom[i] == length[i]))
                  | ((right[i] - left[i] == length[i]) & (top[i] - bottom[i] == width[i])))
    for x, y in itertools.combinations(range(n), 2):
        sep = separation[classes[x] - 1][classes[y] - 1]
        model += ((right[x] + sep <= left[y])
                  | (left[x] >= right[y] + sep)
                  | (top[x] + sep <= bottom[y])
                  | (bottom[x] >= top[y] + sep))
    return model, {"left": [left[i] for i in range(n)],
                   "right": [right[i] for i in range(n)],
                   "top": [top[i] for i in range(n)],
                   "bottom": [bottom[i] for i in range(n)]}
