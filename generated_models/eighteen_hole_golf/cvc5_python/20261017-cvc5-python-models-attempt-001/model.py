# Model for eighteen_hole_golf (cvc5, satisfaction).
# Generate a random 18-hole golf course where each hole has a length of 3, 4, or 5,
# and the total length of the course is 72. Output: the lengths of the holes (holes),
# a list of 18 integers.

import cvc5.pythonic as cz


def build(instance):
    # The description fixes 18 holes and the total length 72; the instance carries no data.
    n_holes = 18
    total = 72

    holes = cz.Ints(" ".join(f"h{i}" for i in range(n_holes)))

    # Each hole has a length of 3, 4, or 5.
    bounds = []
    for h in holes:
        bounds.append(h >= 3)
        bounds.append(h <= 5)

    # The total length of the course is 72.
    total_length = [sum(holes) == total]

    return bounds + total_length, {"holes": list(holes)}
