"""Vessel loading: position rectangular containers on a rectangular deck, in a single layer.

Containers are parallel to the sides of the deck and may be turned a quarter turn. They
must not overlap, and containers of certain classes must be a minimum distance apart.
The model finds positions (left, right, top, bottom) for every container.
"""
from docplex.mp.model import Model


def build(instance):
    deck_width = instance["deck_width"]
    deck_length = instance["deck_length"]
    n = instance["n_containers"]
    width = instance["width"]            # width of each container
    length = instance["length"]          # length of each container
    classes = instance["classes"]        # class of each container, counted from 1
    separation = instance["separation"]  # least distance between containers of two classes

    model = Model("vessel_loading")

    # turned[i] is 1 when container i is turned a quarter turn: its extent along the deck
    # then is its length instead of its width.
    turned = [model.binary_var(name=f"turned_{i}") for i in range(n)]

    # left[i] and bottom[i] are the lower-left corner of container i on the deck.
    left = [model.integer_var(0, deck_width, name=f"left_{i}") for i in range(n)]
    bottom = [model.integer_var(0, deck_length, name=f"bottom_{i}") for i in range(n)]

    # The shape of container i: right - left is its width and top - bottom its length, or the
    # other way round when it is turned.
    right = [left[i] + width[i] + (length[i] - width[i]) * turned[i] for i in range(n)]
    top = [bottom[i] + length[i] - (length[i] - width[i]) * turned[i] for i in range(n)]

    # Every container lies on the deck.
    for i in range(n):
        model.add_constraint(right[i] <= deck_width)
        model.add_constraint(top[i] <= deck_length)

    # No two containers overlap, and they keep the separation of their classes: container x is
    # at least `sep` to the left of y, to the right of y, below y or above y. Two binaries p, q
    # choose which of these four holds, as in the table
    #     (p, q) = (0, 0): x left of y     (1, 0): y left of x
    #              (0, 1): x below y       (1, 1): y below x
    # Each row below is relaxed by a bound times a factor that is at least 1, except for its
    # own choice, where the factor is 0. The bound is the largest the left-hand side can be, so
    # a relaxed row never binds.
    for x in range(n):
        for y in range(x + 1, n):
            sep = separation[classes[x] - 1][classes[y] - 1]
            across = deck_width + sep    # largest value of a left-right gap term
            along = deck_length + sep    # largest value of a top-bottom gap term
            p = model.binary_var(name=f"p_{x}_{y}")
            q = model.binary_var(name=f"q_{x}_{y}")
            model.add_constraint(right[x] + sep - left[y] <= across * (p + q))
            model.add_constraint(right[y] + sep - left[x] <= across * (1 - p + q))
            model.add_constraint(top[x] + sep - bottom[y] <= along * (1 + p - q))
            model.add_constraint(top[y] + sep - bottom[x] <= along * (2 - p - q))

    return model, {"left": left, "right": right, "top": top, "bottom": bottom}
