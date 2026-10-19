# Vessel loading (CSPLib prob008): position single-layer cuboid containers, parallel to the
# sides of a rectangular deck, so that they do not overlap and the separation constraints
# between container classes hold. Each container may be placed in either orientation.
# The output "top" is the upper edge of a container and "bottom" its lower edge.
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
    lower = [cz.Int(f"lower_{i}") for i in range(n)]
    right = [cz.Int(f"right_{i}") for i in range(n)]
    upper = [cz.Int(f"upper_{i}") for i in range(n)]
    rot = [cz.Bool(f"rot_{i}") for i in range(n)]

    s = cz.SolverFor("QF_LIA")

    # each container is placed in one orientation; a rotated container swaps its extents
    for i in range(n):
        s.add(cz.Implies(rot[i], cz.And(right[i] - left[i] == cl[i], upper[i] - lower[i] == cw[i])))
        s.add(cz.Implies(cz.Not(rot[i]), cz.And(right[i] - left[i] == cw[i], upper[i] - lower[i] == cl[i])))

    # containers lie on the deck
    for i in range(n):
        s.add(left[i] >= 0, lower[i] >= 0, right[i] <= deck_w, upper[i] <= deck_l)

    # containers do not overlap, and classes that need a minimum distance keep it,
    # either along the deck or across the deck
    for i in range(n):
        for j in range(i + 1, n):
            d = sep[classes[i] - 1][classes[j] - 1]
            p = [cz.Bool(f"p_{i}_{j}_{k}") for k in range(4)]
            s.add(cz.Or(*p))
            s.add(cz.Implies(p[0], right[i] + d <= left[j]))
            s.add(cz.Implies(p[1], right[j] + d <= left[i]))
            s.add(cz.Implies(p[2], upper[i] + d <= lower[j]))
            s.add(cz.Implies(p[3], upper[j] + d <= lower[i]))

    outputs = {"left": left, "right": right, "top": upper, "bottom": lower}
    return s, outputs
