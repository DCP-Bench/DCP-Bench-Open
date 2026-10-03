"""Vessel loading: place rectangular containers on a rectangular deck, each parallel to
the deck sides (it may be turned by 90 degrees), without overlap, and keeping the
minimum separation required between the classes of every two containers.

The model reports, for each container, its left and right x-coordinates and its bottom
and top y-coordinates.
"""
import pulp


def build(instance):
    deck_width = instance["deck_width"]
    deck_length = instance["deck_length"]
    n = instance["n_containers"]
    width = instance["width"]
    length = instance["length"]
    classes = instance["classes"]
    separation = instance["separation"]  # separation[c1-1][c2-1] = minimum gap between classes c1 and c2

    problem = pulp.LpProblem("vessel_loading", pulp.LpMinimize)  # satisfaction: no objective

    # The deck is a grid of unit cells (x, y), 0 <= x < deck_width, 0 <= y < deck_length.
    # Container i is placed by choosing its extent (width x length, or length x width
    # when turned by 90 degrees) and the cell of its left-bottom corner:
    # place[i][(w, h, x, y)] = 1 if container i occupies the cells x..x+w-1, y..y+h-1.
    # Choosing a placement directly and counting cells (instead of comparing every two
    # containers with four big-M disjunctions) keeps the relaxation tight on a crowded deck.
    place = []
    for i in range(n):
        shapes = [(width[i], length[i])]
        if width[i] != length[i]:  # a square looks the same turned
            shapes.append((length[i], width[i]))
        options = {}
        for w, h in shapes:
            for x in range(deck_width - w + 1):
                for y in range(deck_length - h + 1):
                    options[(w, h, x, y)] = pulp.LpVariable(f"place_{i}_{w}x{h}_{x}_{y}", cat="Binary")
        place.append(options)
        # each container has exactly one placement
        problem += pulp.lpSum(options.values()) == 1

    # No overlap: each cell of the deck is covered by at most one container.
    # cover[(i, cx, cy)] = the placements of container i that include the cell (cx, cy).
    cover = {}
    for i in range(n):
        for cx in range(deck_width):
            for cy in range(deck_length):
                cover[(i, cx, cy)] = [var for (w, h, x, y), var in place[i].items()
                                      if x <= cx < x + w and y <= cy < y + h]
    for cx in range(deck_width):
        for cy in range(deck_length):
            problem += pulp.lpSum(var for i in range(n) for var in cover[(i, cx, cy)]) <= 1

    # Separation: containers a and b whose classes need a minimum gap sep > 0 (separations
    # are non-negative) are at least sep apart along the deck or across it. They violate
    # that exactly when a cell of b lies inside a's footprint grown by sep in every
    # direction. So for every cell: if b covers it, a's grown footprint must not contain
    # it. `grown` is the placements of a whose grown footprint contains the cell (at most
    # one of them is used, a being placed once).
    for a in range(n):
        for b in range(a + 1, n):
            sep = separation[classes[a] - 1][classes[b] - 1]
            if sep <= 0:
                continue
            for cx in range(deck_width):
                for cy in range(deck_length):
                    grown = [var for (w, h, x, y), var in place[a].items()
                             if x - sep <= cx <= x + w - 1 + sep and y - sep <= cy <= y + h - 1 + sep]
                    problem += pulp.lpSum(grown) + pulp.lpSum(cover[(b, cx, cy)]) <= 1

    # Coordinates reported: left/bottom is the corner cell; right/top add the extent.
    left = [pulp.lpSum(x * var for (w, h, x, y), var in place[i].items()) for i in range(n)]
    bottom = [pulp.lpSum(y * var for (w, h, x, y), var in place[i].items()) for i in range(n)]
    right = [pulp.lpSum((x + w) * var for (w, h, x, y), var in place[i].items()) for i in range(n)]
    top = [pulp.lpSum((y + h) * var for (w, h, x, y), var in place[i].items()) for i in range(n)]

    return problem, {"left": left, "right": right, "top": top, "bottom": bottom}
