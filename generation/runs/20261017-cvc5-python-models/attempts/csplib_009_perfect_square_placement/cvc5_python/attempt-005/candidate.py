# Perfect square placement (squared square problem): pack the squares with the given
# integer sides into a bigger square of side `base`, so that the squares do not
# overlap and all square borders are parallel to the border of the big square.
# Coordinates start from 0.
#
# This attempt uses a placement encoding: each square has one Boolean per position
# where its lower-left corner can be, the squares choose exactly one position, and
# every unit cell of the big square is covered by exactly one chosen square.
import cvc5.pythonic as cz


def build(instance):
    base = instance["base"]
    sides = instance["sides"]
    n = len(sides)
    xs = [cz.Int(f"x{i}") for i in range(n)]
    ys = [cz.Int(f"y{i}") for i in range(n)]

    constraints = []

    # Every square lies inside the big square: its corner is at 0 or more and its
    # far border is at most base. The placement Booleans below only exist for
    # positions inside the big square.
    placements = []  # placements[i] = list of (x, y, Bool)
    for i in range(n):
        s = sides[i]
        choices = []
        for px in range(base - s + 1):
            for py in range(base - s + 1):
                choices.append((px, py, cz.Bool(f"p{i}_{px}_{py}")))
        placements.append(choices)

    # Each square is placed at exactly one position, and its coordinates are that
    # position.
    for i in range(n):
        bools = [b for _, _, b in placements[i]]
        constraints.append(cz.Or(*bools))
        constraints.append(cz.Sum([cz.If(b, 1, 0) for b in bools]) == 1)
        constraints.append(
            xs[i] == cz.Sum([cz.If(b, px, 0) for px, _, b in placements[i]])
        )
        constraints.append(
            ys[i] == cz.Sum([cz.If(b, py, 0) for _, py, b in placements[i]])
        )

    # No two squares overlap each other, and no spare capacity: every unit cell of
    # the big square is covered by exactly one square. The cell is covered by a
    # square when the square's chosen corner lies so that the cell is inside it.
    for cx in range(base):
        for cy in range(base):
            covering = []
            for i in range(n):
                s = sides[i]
                for px, py, b in placements[i]:
                    if px <= cx < px + s and py <= cy < py + s:
                        covering.append(cz.If(b, 1, 0))
            if not covering:
                constraints.append(False)
            else:
                constraints.append(cz.Sum(covering) == 1)

    return constraints, {"x_coords": xs, "y_coords": ys}
