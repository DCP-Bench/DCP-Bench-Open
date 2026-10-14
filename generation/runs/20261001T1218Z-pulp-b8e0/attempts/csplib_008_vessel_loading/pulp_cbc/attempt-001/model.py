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

    # Container i occupies [left[i], right[i]] x [bottom[i], top[i]]. Its extent is
    # width x length or, turned by 90 degrees, length x width, so each coordinate is
    # at least the smaller side away from the deck edge it faces.
    side = [min(width[i], length[i]) for i in range(n)]
    left = [pulp.LpVariable(f"left_{i}", 0, deck_width - side[i], cat="Integer") for i in range(n)]
    right = [pulp.LpVariable(f"right_{i}", side[i], deck_width, cat="Integer") for i in range(n)]
    bottom = [pulp.LpVariable(f"bottom_{i}", 0, deck_length - side[i], cat="Integer") for i in range(n)]
    top = [pulp.LpVariable(f"top_{i}", side[i], deck_length, cat="Integer") for i in range(n)]

    # Shape of each container: turned[i] = 1 if container i is turned by 90 degrees, so
    # that its horizontal extent is length[i] and its vertical extent is width[i].
    # A square container looks the same turned, so it is kept unturned: this only
    # removes a duplicate that gives the same coordinates.
    turned = [pulp.LpVariable(f"turned_{i}", cat="Binary") for i in range(n)]
    for i in range(n):
        problem += right[i] - left[i] == width[i] + (length[i] - width[i]) * turned[i]
        problem += top[i] - bottom[i] == length[i] + (width[i] - length[i]) * turned[i]
        if width[i] == length[i]:
            problem += turned[i] == 0

    # No two containers overlap, and the classes' separation is kept: for each pair
    # (x, y) one of four relations holds: x is left of y, x is right of y, x is below y,
    # or x is above y, each with a gap of at least sep. apart[(x, y)][k] = 1 if relation
    # k is the one used. A relation that is not used is relaxed by a big-M equal to the
    # largest value its left-hand side can exceed its right-hand side by (the deck extent
    # plus sep).
    for x in range(n):
        for y in range(x + 1, n):
            sep = separation[classes[x] - 1][classes[y] - 1]
            apart = [pulp.LpVariable(f"apart_{x}_{y}_{k}", cat="Binary") for k in range(4)]
            m_across = deck_width + sep
            m_along = deck_length + sep
            # x at least sep left of y
            problem += right[x] + sep <= left[y] + m_across * (1 - apart[0])
            # x at least sep right of y
            problem += right[y] + sep <= left[x] + m_across * (1 - apart[1])
            # x at least sep under y
            problem += top[x] + sep <= bottom[y] + m_along * (1 - apart[2])
            # x at least sep above y
            problem += top[y] + sep <= bottom[x] + m_along * (1 - apart[3])
            problem += pulp.lpSum(apart) >= 1

    return problem, {"left": left, "right": right, "top": top, "bottom": bottom}
