# Vessel loading: place rectangular containers on a rectangular deck, in a single layer and
# parallel to the deck sides (each may be turned a quarter turn), so that none overlap and
# containers of classes with a separation requirement keep that minimum distance apart.
from exact import Exact


def build(instance):
    deck_width = instance["deck_width"]
    deck_length = instance["deck_length"]
    width = instance["width"]  # width of each container
    length = instance["length"]  # length of each container
    classes = instance["classes"]  # class (1-based) of each container
    separation = instance["separation"]  # minimum distance between two classes (class 1 = row 0)
    n = len(width)

    solver = Exact()

    # container i covers left[i]..right[i] across the deck and bottom[i]..top[i] along it
    left = [f"left_{i}" for i in range(n)]
    right = [f"right_{i}" for i in range(n)]
    top = [f"top_{i}" for i in range(n)]
    bottom = [f"bottom_{i}" for i in range(n)]
    for i in range(n):
        solver.addVariable(left[i], 0, deck_width)
        solver.addVariable(right[i], 0, deck_width)
        solver.addVariable(top[i], 0, deck_length)
        solver.addVariable(bottom[i], 0, deck_length)

    # a container has its given shape, either as listed or turned by a quarter. turned[i] = 1
    # means the container is turned; then it is length wide and width long, otherwise width
    # wide and length long. Turning is a 0/1 switch inside two linear equalities.
    for i in range(n):
        turned = f"turned_{i}"
        solver.addVariable(turned, 0, 1)
        turn_effect = [(-(length[i] - width[i]), turned)] if length[i] != width[i] else []
        solver.addConstraint([(1, right[i]), (-1, left[i])] + turn_effect, True, width[i], True, width[i])
        turn_effect = [(-(width[i] - length[i]), turned)] if length[i] != width[i] else []
        solver.addConstraint([(1, top[i]), (-1, bottom[i])] + turn_effect, True, length[i], True, length[i])

    # no two containers overlap, and classes keep their separation: for every pair, container x
    # is at least sep to the left of, to the right of, below, or above container y.
    # Each of the four cases gets a 0/1 variable that is 1 exactly when the case holds, and at
    # least one must hold.
    for x in range(n):
        for y in range(x + 1, n):
            sep = separation[classes[x] - 1][classes[y] - 1]
            cases = []
            for label, terms in (
                ("left_of", [(1, left[y]), (-1, right[x])]),  # right[x] + sep <= left[y]
                ("right_of", [(1, left[x]), (-1, right[y])]),  # left[x] >= right[y] + sep
                ("under", [(1, bottom[y]), (-1, top[x])]),  # top[x] + sep <= bottom[y]
                ("above", [(1, bottom[x]), (-1, top[y])]),  # bottom[x] >= top[y] + sep
            ):
                case = f"container_{x}_{label}_{y}"
                solver.addVariable(case, 0, 1)
                solver.addReification(case, True, terms, sep)
                cases.append((1, case))
            solver.addConstraint(cases, True, 1)

    return solver, {"left": left, "right": right, "top": top, "bottom": bottom}
