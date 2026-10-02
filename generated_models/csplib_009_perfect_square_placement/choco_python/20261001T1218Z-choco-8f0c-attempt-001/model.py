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

    return model, {"x_coords": x_coords, "y_coords": y_coords}
