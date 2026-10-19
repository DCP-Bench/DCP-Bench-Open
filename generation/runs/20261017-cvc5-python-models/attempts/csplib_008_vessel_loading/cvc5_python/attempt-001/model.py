# Vessel loading (CSPLib prob008): position single-layer cuboid containers, parallel to the
# sides of a rectangular deck, so that they do not overlap and the separation constraints
# between container classes hold. Each container may be rotated by 90 degrees.
import cvc5.pythonic as cz


def build(instance):
    n = instance["n_containers"]
    deck_w = instance["deck_width"]
    deck_l = instance["deck_length"]
    cw = instance["width"]
    cl = instance["length"]
    classes = instance["classes"]
    sep = instance["separation"]

    left = [cz.Int(f"left_{i}") for i in range(n)]
    top = [cz.Int(f"top_{i}") for i in range(n)]
    rot = [cz.Bool(f"rot_{i}") for i in range(n)]

    # Extent along the deck width and length; a rotated container swaps them.
    ext_w = [cz.If(rot[i], cz.IntVal(cl[i]), cz.IntVal(cw[i])) for i in range(n)]
    ext_l = [cz.If(rot[i], cz.IntVal(cw[i]), cz.IntVal(cl[i])) for i in range(n)]
    right = [left[i] + ext_w[i] for i in range(n)]
    bottom = [top[i] + ext_l[i] for i in range(n)]

    s = cz.SolverFor("QF_LIA")

    # containers lie on the deck
    for i in range(n):
        s.add(left[i] >= 0, top[i] >= 0, right[i] <= deck_w, bottom[i] <= deck_l)

    # containers do not overlap, and classes that need a minimum distance keep it,
    # either along the deck or across the deck
    for i in range(n):
        for j in range(i + 1, n):
            d = sep[classes[i] - 1][classes[j] - 1]
            s.add(
                cz.Or(
                    right[i] + d <= left[j],
                    right[j] + d <= left[i],
                    bottom[i] + d <= top[j],
                    bottom[j] + d <= top[i],
                )
            )

    outputs = {"left": left, "right": right, "top": top, "bottom": bottom}
    return s, outputs
