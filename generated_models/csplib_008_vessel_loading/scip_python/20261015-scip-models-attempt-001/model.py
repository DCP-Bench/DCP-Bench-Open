# Vessel loading: place rectangular containers without overlap on a rectangular deck,
# keeping containers of separated classes at least the required distance apart.
from pyscipopt import Model, quicksum


def build(instance):
    W = instance["deck_width"]
    L = instance["deck_length"]
    n = instance["n_containers"]
    width = instance["width"]
    length = instance["length"]
    classes = instance["classes"]
    sep = instance["separation"]

    m = Model()

    # each container may lie either way round: rot[i] = 1 swaps its width and length
    rot = [m.addVar(name=f"rot_{i}", vtype="B") for i in range(n)]
    # extent of container i along the deck width (x) and deck length (y), linear in rot[i]
    dx = [width[i] + (length[i] - width[i]) * rot[i] for i in range(n)]
    dy = [length[i] + (width[i] - length[i]) * rot[i] for i in range(n)]

    # left/bottom corner of container i; it must fit on the deck in either orientation
    left = [m.addVar(name=f"left_{i}", vtype="I", lb=0, ub=W - min(width[i], length[i])) for i in range(n)]
    bottom = [m.addVar(name=f"bottom_{i}", vtype="I", lb=0, ub=L - min(width[i], length[i])) for i in range(n)]
    right = [left[i] + dx[i] for i in range(n)]
    top = [bottom[i] + dy[i] for i in range(n)]

    # the container fits on the deck: its right and top edges stay within the deck
    for i in range(n):
        m.addCons(right[i] <= W)
        m.addCons(top[i] <= L)

    # for each pair of containers, a binary selects which of four separations holds:
    # i left of j, j left of i, i below j, or j below i
    for i in range(n):
        for j in range(i + 1, n):
            # minimum distance required between the classes of i and j (0 if none)
            s = sep[classes[i] - 1][classes[j] - 1]
            p = [m.addVar(name=f"p_{i}_{j}_{k}", vtype="B") for k in range(4)]
            # exactly one of the four separations is chosen for this pair
            m.addCons(quicksum(p) == 1)
            # no overlap and the required separation: the chosen separation holds
            m.addConsIndicator(right[i] + s <= left[j], binvar=p[0])
            m.addConsIndicator(right[j] + s <= left[i], binvar=p[1])
            m.addConsIndicator(top[i] + s <= bottom[j], binvar=p[2])
            m.addConsIndicator(top[j] + s <= bottom[i], binvar=p[3])

    return m, {"left": left, "right": right, "top": top, "bottom": bottom}
