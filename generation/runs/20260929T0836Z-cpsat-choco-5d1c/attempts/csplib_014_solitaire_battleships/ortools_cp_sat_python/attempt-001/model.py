# Solitaire battleships: fill a grid with water, submarines and ship parts
# (left, right, top, bottom, middle) so that the fleet, the row and column
# totals and the given hints all hold, and no two ships touch, not even
# diagonally.
from ortools.sat.python import cp_model


def build(instance):
    rows, cols = instance["rows"], instance["cols"]
    rowsum, colsum = instance["rowsum"], instance["colsum"]  # occupied cells per row / column
    fleet = instance["fleet_counts"]  # [ship size, how many] pairs
    hints = instance["hints"]  # [row, column, cell value] shots already taken
    # the cell codes come with the instance
    WATER, CIRCLE = instance["WATER"], instance["CIRCLE"]
    LEFT, RIGHT, TOP, BOTTOM, MIDDLE = (instance[k] for k in ("LEFT", "RIGHT", "TOP", "BOTTOM", "MIDDLE"))

    model = cp_model.CpModel()

    # A cell is water, a submarine or one of five ship parts, so the generic
    # "ship" code the encoding also lists is left out. is_[t][r][c] is true when
    # cell (r, c) holds code t (a one-hot encoding of the cell).
    codes = [WATER, CIRCLE, LEFT, RIGHT, TOP, BOTTOM, MIDDLE]
    is_ = {t: [[model.new_bool_var(f"is{t}_{r}_{c}") for c in range(cols)] for r in range(rows)] for t in codes}
    grid = [[model.new_int_var(0, max(codes), f"grid_{r}_{c}") for c in range(cols)] for r in range(rows)]
    for r in range(rows):
        for c in range(cols):
            model.add_exactly_one(is_[t][r][c] for t in codes)
            model.add(grid[r][c] == sum(t * is_[t][r][c] for t in codes))

    def occupied(r, c):
        return is_[WATER][r][c].negated()

    def require(cell, neighbours_water, one_of=None):
        """Cell literal implies the listed neighbours are water and (optionally) one
        neighbour holds one of the given codes; an off-grid neighbour is water, and
        cannot hold a code."""
        for (nr, nc) in neighbours_water:
            if 0 <= nr < rows and 0 <= nc < cols:
                model.add_implication(cell, is_[WATER][nr][nc])
        if one_of is not None:
            (nr, nc), allowed = one_of
            if 0 <= nr < rows and 0 <= nc < cols:
                model.add_bool_or([is_[t][nr][nc] for t in allowed]).only_enforce_if(cell)
            else:
                model.add_bool_or([]).only_enforce_if(cell)  # impossible: no room for the rest of the ship

    # the shots that were already taken
    for r, c, value in hints:
        model.add(grid[r][c] == value)

    # each row and column holds the stated number of ship cells
    for r in range(rows):
        model.add(sum(occupied(r, c) for c in range(cols)) == rowsum[r])
    for c in range(cols):
        model.add(sum(occupied(r, c) for r in range(rows)) == colsum[c])

    for r in range(rows):
        for c in range(cols):
            # ships never touch diagonally: all four diagonal neighbours of a ship cell are water
            for (nr, nc) in [(r - 1, c - 1), (r - 1, c + 1), (r + 1, c - 1), (r + 1, c + 1)]:
                if 0 <= nr < rows and 0 <= nc < cols:
                    model.add_implication(occupied(r, c), is_[WATER][nr][nc])

            # a submarine is surrounded by water
            require(is_[CIRCLE][r][c], [(r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)])
            # the left end of a ship continues to the right and has water on its other three sides
            require(is_[LEFT][r][c], [(r, c - 1), (r - 1, c), (r + 1, c)],
                    one_of=((r, c + 1), [MIDDLE, RIGHT]))
            # the right end continues to the left
            require(is_[RIGHT][r][c], [(r, c + 1), (r - 1, c), (r + 1, c)],
                    one_of=((r, c - 1), [MIDDLE, LEFT]))
            # the top end continues downwards
            require(is_[TOP][r][c], [(r - 1, c), (r, c - 1), (r, c + 1)],
                    one_of=((r + 1, c), [MIDDLE, BOTTOM]))
            # the bottom end continues upwards
            require(is_[BOTTOM][r][c], [(r + 1, c), (r, c - 1), (r, c + 1)],
                    one_of=((r - 1, c), [MIDDLE, TOP]))

            # a middle part lies inside a horizontal ship (ship cells to its left
            # and right, water above and below) or a vertical one (the same turned
            # a quarter)
            horizontal = model.new_bool_var(f"horizontal_{r}_{c}")
            vertical = model.new_bool_var(f"vertical_{r}_{c}")
            model.add_bool_or([horizontal, vertical]).only_enforce_if(is_[MIDDLE][r][c])
            if 0 < c < cols - 1:
                model.add_bool_or([is_[LEFT][r][c - 1], is_[MIDDLE][r][c - 1]]).only_enforce_if(horizontal)
                model.add_bool_or([is_[RIGHT][r][c + 1], is_[MIDDLE][r][c + 1]]).only_enforce_if(horizontal)
                for (nr, nc) in [(r - 1, c), (r + 1, c)]:
                    if 0 <= nr < rows:
                        model.add_implication(horizontal, is_[WATER][nr][nc])
            else:
                model.add(horizontal == 0)
            if 0 < r < rows - 1:
                model.add_bool_or([is_[TOP][r - 1][c], is_[MIDDLE][r - 1][c]]).only_enforce_if(vertical)
                model.add_bool_or([is_[BOTTOM][r + 1][c], is_[MIDDLE][r + 1][c]]).only_enforce_if(vertical)
                for (nr, nc) in [(r, c - 1), (r, c + 1)]:
                    if 0 <= nc < cols:
                        model.add_implication(vertical, is_[WATER][nr][nc])
            else:
                model.add(vertical == 0)

    # fleet: the required number of ships of each size
    n_ships = 0
    for size, count in fleet:
        n_ships += count if size > 1 else 0
        if size == 1:
            # submarines are single cells
            model.add(sum(is_[CIRCLE][r][c] for r in range(rows) for c in range(cols)) == count)
            continue
        # a ship of this size is an end part, size-2 middle parts and the other end, in a line
        placed = []
        for r in range(rows):
            for c in range(cols - size + 1):
                cells = [is_[LEFT][r][c], is_[RIGHT][r][c + size - 1]] + [is_[MIDDLE][r][c + k] for k in range(1, size - 1)]
                ship = model.new_bool_var(f"ship_h_{size}_{r}_{c}")
                model.add_bool_and(cells).only_enforce_if(ship)
                model.add_bool_or([x.negated() for x in cells]).only_enforce_if(ship.negated())
                placed.append(ship)
        for r in range(rows - size + 1):
            for c in range(cols):
                cells = [is_[TOP][r][c], is_[BOTTOM][r + size - 1][c]] + [is_[MIDDLE][r + k][c] for k in range(1, size - 1)]
                ship = model.new_bool_var(f"ship_v_{size}_{r}_{c}")
                model.add_bool_and(cells).only_enforce_if(ship)
                model.add_bool_or([x.negated() for x in cells]).only_enforce_if(ship.negated())
                placed.append(ship)
        model.add(sum(placed) == count)

    # no ship of a size the fleet does not list: every left or top end starts one of the ships counted above
    model.add(
        sum(is_[LEFT][r][c] + is_[TOP][r][c] for r in range(rows) for c in range(cols)) == n_ships
    )

    return model, {"grid": grid}
