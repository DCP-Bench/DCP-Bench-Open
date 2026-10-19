# csplib_008_vessel_loading (CSPLib prob008, vessel loading).
# Decide whether the containers can be placed on the deck without overlap and with the class separations.
# Cell-based model: each container picks exactly one placement (orientation, left, bottom) inside the deck.
# Each deck cell is covered by at most one placement over all containers.
import mip


def build(instance):
    W = instance["deck_width"]
    L = instance["deck_length"]
    n = instance["n_containers"]
    widths = instance["width"]
    lengths = instance["length"]
    classes = instance["classes"]
    sep = instance["separation"]

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # Steps: every container side and every positive separation value.
    steps = set(widths) | set(lengths)
    for row in sep:
        for val in row:
            if val > 0:
                steps.add(val)

    # Corner positions: a container can be pushed left (down) until it touches the deck edge or
    # another container plus a side or separation gap, so every left (bottom) value is a sum of steps.
    def reachable(limit):
        reach = {0}
        frontier = [0]
        while frontier:
            p = frontier.pop()
            for s in steps:
                q = p + s
                if q <= limit and q not in reach:
                    reach.add(q)
                    frontier.append(q)
        return sorted(reach)

    xs = reachable(W)
    ys = reachable(L)

    # One binary per (container, orientation, left, bottom) that fits inside the deck.
    # A square container has one orientation only.
    placements = []
    for i in range(n):
        w = widths[i]
        l = lengths[i]
        orients = [(w, l)] if w == l else [(w, l), (l, w)]
        plist = []
        for (ew, eh) in orients:
            for x0 in xs:
                if x0 + ew > W:
                    continue
                for y0 in ys:
                    if y0 + eh > L:
                        continue
                    v = model.add_var(name=f"p_{i}_{ew}_{eh}_{x0}_{y0}", var_type=mip.BINARY)
                    plist.append((ew, eh, x0, y0, v))
        placements.append(plist)
        # the description: each container is positioned once
        # container i is placed exactly once
        model.add_constr(mip.xsum([t[4] for t in plist]) == 1, name=f"place_{i}")

    # No overlap: each deck cell is covered by at most one placement over all containers.
    for cx in range(W):
        for cy in range(L):
            terms = []
            for i in range(n):
                for (ew, eh, x0, y0, v) in placements[i]:
                    if x0 <= cx < x0 + ew and y0 <= cy < y0 + eh:
                        terms.append(v)
            if len(terms) > 1:
                model.add_constr(mip.xsum(terms) <= 1, name=f"cell_{cx}_{cy}")

    # Separation: containers of classes with separation s must be at least s apart,
    # either along the deck or across it. Container j may not occupy any cell of
    # container i's footprint grown by s on every side. The gap relation is symmetric,
    # so one direction per pair suffices. Classes are numbered from 1 in the data.
    # The separation matrix is indexed by class - 1.
    for i in range(n):
        for j in range(i + 1, n):
            s = max(sep[classes[i] - 1][classes[j] - 1], sep[classes[j] - 1][classes[i] - 1])
            if s <= 0:
                continue
            for cx in range(W):
                for cy in range(L):
                    grown = []
                    for (ew, eh, x0, y0, v) in placements[i]:
                        if x0 - s <= cx < x0 + ew + s and y0 - s <= cy < y0 + eh + s:
                            grown.append(v)
                    cover = []
                    for (ew, eh, x0, y0, v) in placements[j]:
                        if x0 <= cx < x0 + ew and y0 <= cy < y0 + eh:
                            cover.append(v)
                    if grown and cover:
                        model.add_constr(mip.xsum(grown) + mip.xsum(cover) <= 1,
                                         name=f"sep_{i}_{j}_{cx}_{cy}")

    # Output: positions as integer variables tied to the placement binaries.
    # right and top are exclusive edges (left + width, bottom + length).
    left = []
    right = []
    top = []
    bottom = []
    for i in range(n):
        lv = model.add_var(name=f"left_{i}", lb=0, ub=W, var_type=mip.INTEGER)
        rv = model.add_var(name=f"right_{i}", lb=0, ub=W, var_type=mip.INTEGER)
        tv = model.add_var(name=f"top_{i}", lb=0, ub=L, var_type=mip.INTEGER)
        bv = model.add_var(name=f"bottom_{i}", lb=0, ub=L, var_type=mip.INTEGER)
        model.add_constr(lv == mip.xsum([x0 * v for (ew, eh, x0, y0, v) in placements[i]]), name=f"left_def_{i}")
        model.add_constr(rv == mip.xsum([(x0 + ew) * v for (ew, eh, x0, y0, v) in placements[i]]), name=f"right_def_{i}")
        model.add_constr(bv == mip.xsum([y0 * v for (ew, eh, x0, y0, v) in placements[i]]), name=f"bottom_def_{i}")
        model.add_constr(tv == mip.xsum([(y0 + eh) * v for (ew, eh, x0, y0, v) in placements[i]]), name=f"top_def_{i}")
        left.append(lv)
        right.append(rv)
        top.append(tv)
        bottom.append(bv)

    outputs = {"left": left, "right": right, "top": top, "bottom": bottom}
    return model, outputs
