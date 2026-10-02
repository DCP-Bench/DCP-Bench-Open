# Vessel loading: place rectangular containers (which may be turned through 90
# degrees) in a single layer on a rectangular deck, without overlap and keeping
# the minimum distance required between containers of certain classes.
from pychoco.model import Model


def build(instance):
    deck_width = instance["deck_width"]
    deck_length = instance["deck_length"]
    n_containers = instance["n_containers"]
    width = instance["width"]  # width of each container
    length = instance["length"]  # length of each container
    classes = instance["classes"]  # class of each container (1-based)
    separation = instance["separation"]  # separation[c1-1][c2-1] = minimum distance between classes c1 and c2

    model = Model()

    # left[i], right[i] = the sides of container i across the deck (within the deck width)
    left = [model.intvar(0, deck_width, name=f"left_{i}") for i in range(n_containers)]
    right = [model.intvar(0, deck_width, name=f"right_{i}") for i in range(n_containers)]
    # bottom[i], top[i] = the sides of container i along the deck (within the deck length)
    bottom = [model.intvar(0, deck_length, name=f"bottom_{i}") for i in range(n_containers)]
    top = [model.intvar(0, deck_length, name=f"top_{i}") for i in range(n_containers)]

    # Shape of each container: its extent across the deck (right - left) and along the
    # deck (top - bottom) are its width and length, or its length and width when turned.
    # The two orientations are listed as the allowed pairs of extents in a table.
    for i in range(n_containers):
        across = model.intvar(0, deck_width, name=f"across_{i}")
        along = model.intvar(0, deck_length, name=f"along_{i}")
        orientations = [[width[i], length[i]]]
        if width[i] != length[i]:
            orientations.append([length[i], width[i]])
        model.table([across, along], orientations).post()
        model.arithm(left[i], "+", across, "=", right[i]).post()
        model.arithm(bottom[i], "+", along, "=", top[i]).post()

    # No overlap between containers, and containers of classes with a separation
    # requirement are at least that far apart: for each pair of containers x, y,
    # x is at least sep to the left of y, or to the right of y, or below y, or above y.
    for x in range(n_containers):
        for y in range(x + 1, n_containers):
            sep = separation[classes[x] - 1][classes[y] - 1]
            model.or_([
                model.arithm(right[x], "-", left[y], "<=", -sep),  # x left of y
                model.arithm(right[y], "-", left[x], "<=", -sep),  # y left of x
                model.arithm(top[x], "-", bottom[y], "<=", -sep),  # x below y
                model.arithm(top[y], "-", bottom[x], "<=", -sep),  # y below x
            ]).post()

    return model, {"left": left, "right": right, "top": top, "bottom": bottom}
