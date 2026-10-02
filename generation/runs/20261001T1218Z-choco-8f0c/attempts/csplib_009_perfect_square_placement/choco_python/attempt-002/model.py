# Perfect square placement: pack squares of given integer sides into a larger
# square without overlap, with no spare room (their areas sum to the base area).
from pychoco.model import Model


def build(instance):
    base = instance["base"]  # side length of the large square
    sides = instance["sides"]  # side lengths of the small squares
    n = len(sides)

    model = Model()

    # (x_coords[i], y_coords[i]) = lower-left corner of square i. The upper bound
    # base - sides[i] is the "square must stay inside the large square" rule.
    x_coords = [model.intvar(0, base - sides[i], name=f"x_{i}") for i in range(n)]
    y_coords = [model.intvar(0, base - sides[i], name=f"y_{i}") for i in range(n)]

    # no two squares overlap (diff_n takes the widths and heights as variables,
    # so each fixed side length is passed as a constant variable)
    widths = [model.intvar(s, s) for s in sides]
    heights = [model.intvar(s, s) for s in sides]
    model.diff_n(x_coords, y_coords, widths, heights, True).post()

    # Implied constraints, from the squares' areas adding up to the area of the large
    # square: there is no spare room, so every row of unit cells of the large square
    # is covered completely, and so is every column. A square i covers the row at
    # height h when y_i <= h < y_i + sides[i]. The sides of the squares covering a
    # row (or column) add up to base. These equalities let the solver see early that a
    # partial placement leaves a gap it cannot fill.
    if sum(s * s for s in sides) == base * base:
        for coords in (y_coords, x_coords):
            for h in range(base):
                covering = []
                weights = []
                for i in range(n):
                    low = max(0, h - sides[i] + 1)
                    high = min(h, base - sides[i])
                    if low <= high:
                        covering.append(model.member(coords[i], lb=low, ub=high).reify())
                        weights.append(sides[i])
                model.scalar(covering, weights, "=", base).post()

    return model, {"x_coords": x_coords, "y_coords": y_coords}
