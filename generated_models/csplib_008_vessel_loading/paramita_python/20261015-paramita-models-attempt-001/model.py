from paramita.modelling import Bool, If, Or


# Vessel loading decision problem (CSPLib prob008): place rectangular containers
# in a single layer on a rectangular deck, without overlap and respecting the
# minimum separation between classes. Containers may be turned by 90 degrees.
def build(instance):
    dw, dl = instance["deck_width"], instance["deck_length"]
    n = instance["n_containers"]
    width, length = instance["width"], instance["length"]
    classes, sep = instance["classes"], instance["separation"]

    # rot[c] = 1 if container c is turned (its width lies along the deck length);
    # a square container gains nothing from turning, so it has no flag
    rot = [Bool(f"rotated_{c}") if width[c] != length[c] else 0 for c in range(n)]

    # left[c][v] = 1 if container c has its left edge at x = v (one-hot over the positions it can take)
    # bottom[c][v] = 1 if container c has its bottom edge at y = v (one-hot over the positions it can take)
    left_b = [{v: Bool(f"left_{c}_{v}") for v in range(dw - min(width[c], length[c]) + 1)} for c in range(n)]
    bottom_b = [{v: Bool(f"bottom_{c}_{v}") for v in range(dl - min(width[c], length[c]) + 1)} for c in range(n)]

    cons = []

    # every container gets exactly one left and one bottom position
    cons += [sum(left_b[c].values()) == 1 for c in range(n)]
    cons += [sum(bottom_b[c].values()) == 1 for c in range(n)]

    left = [sum(v * b for v, b in left_b[c].items()) for c in range(n)]
    bottom = [sum(v * b for v, b in bottom_b[c].items()) for c in range(n)]
    right = [left[c] + width[c] + (length[c] - width[c]) * rot[c] for c in range(n)]
    top = [bottom[c] + length[c] + (width[c] - length[c]) * rot[c] for c in range(n)]

    # every container lies within the deck
    cons += [right[c] <= dw for c in range(n)]
    cons += [top[c] <= dl for c in range(n)]

    # containers do not overlap, and containers of separated classes keep their minimum distance,
    # either along the deck (left-right) or across the deck (bottom-top)
    for i in range(n):
        for j in range(i + 1, n):
            s = sep[classes[i] - 1][classes[j] - 1]
            alts = [
                right[i] + s <= left[j],
                right[j] + s <= left[i],
                top[i] + s <= bottom[j],
                top[j] + s <= bottom[i],
            ]
            ok = [Bool(f"apart_{i}_{j}_{k}") for k in range(4)]
            cons.append(Or(ok))
            cons += [If(ok[k], alts[k]) for k in range(4)]

    return cons, {"left": left, "right": right, "top": top, "bottom": bottom}
