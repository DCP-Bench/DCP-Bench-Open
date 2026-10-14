# Perfect square placement: pack squares of given integer sides into a big
# square with no overlap and no spare room.
import z3


def build(instance):
    base = instance["base"]    # side length of the big square
    sides = instance["sides"]  # side lengths of the small squares
    n = len(sides)

    # (x_coords[i], y_coords[i]) is the lower-left corner of small square i.
    x_coords = [z3.Int(f"x_coords_{i}") for i in range(n)]
    y_coords = [z3.Int(f"y_coords_{i}") for i in range(n)]

    solver = z3.Solver()

    # Every small square lies inside the big square.
    for i in range(n):
        solver.add(x_coords[i] >= 0, x_coords[i] + sides[i] <= base)
        solver.add(y_coords[i] >= 0, y_coords[i] + sides[i] <= base)

    # No two small squares overlap: one is left of, right of, below or above the other.
    for a in range(n):
        for b in range(a + 1, n):
            solver.add(z3.Or(
                x_coords[a] + sides[a] <= x_coords[b],
                x_coords[b] + sides[b] <= x_coords[a],
                y_coords[a] + sides[a] <= y_coords[b],
                y_coords[b] + sides[b] <= y_coords[a]))

    # Implied constraint: the squares' total area equals the big square's area (the
    # problem guarantees this), so no spare room is left and every unit-wide column
    # and row of the big square is covered over its full length by the squares that
    # cross it. Z3 has no Cumulative global, so these sums supply the pruning that it
    # would give. They are written as pseudo-Boolean sums over Booleans that say
    # "square i crosses column (row) `line`", which Z3 handles better than sums of
    # If terms.
    for line in range(base):
        crosses_column = [z3.And(x_coords[i] <= line, line < x_coords[i] + sides[i])
                          for i in range(n)]
        crosses_row = [z3.And(y_coords[i] <= line, line < y_coords[i] + sides[i])
                       for i in range(n)]
        solver.add(z3.PbEq([(crosses_column[i], sides[i]) for i in range(n)], base))
        solver.add(z3.PbEq([(crosses_row[i], sides[i]) for i in range(n)], base))

    return solver, {"x_coords": x_coords, "y_coords": y_coords}
