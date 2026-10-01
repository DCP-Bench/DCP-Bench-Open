# Solitaire Battleships: fill a grid with water and ship parts so that the fleet is
# complete, ships do not touch (not even diagonally), the row and column sums of
# ship cells are met, and the given hints hold.
import cpmpy as cp


def build(instance):
    rows = instance["rows"]
    cols = instance["cols"]
    rowsum = instance["rowsum"]              # number of ship cells in each row
    colsum = instance["colsum"]              # number of ship cells in each column
    # fleet_counts is a list of [ship_size, how_many]
    fleet_counts = {size: count for size, count in instance["fleet_counts"]}
    hints = instance["hints"]                # [row, col, cell value] revealed at the start

    # Cell codes, given by the instance.
    WATER = instance["WATER"]
    CIRCLE = instance["CIRCLE"]              # a one-cell ship (submarine)
    LEFT = instance["LEFT"]                  # left end of a horizontal ship
    RIGHT = instance["RIGHT"]                # right end of a horizontal ship
    TOP = instance["TOP"]                    # top end of a vertical ship
    BOTTOM = instance["BOTTOM"]              # bottom end of a vertical ship
    MIDDLE = instance["MIDDLE"]              # inner cell of a ship of length 3 or more

    grid = cp.intvar(min(WATER, CIRCLE, LEFT, RIGHT, TOP, BOTTOM, MIDDLE),
                     max(WATER, CIRCLE, LEFT, RIGHT, TOP, BOTTOM, MIDDLE),
                     shape=(rows, cols), name="grid")

    def one_of(r, c, kinds):
        """Condition 'cell (r, c) holds one of `kinds`'. Cells outside the grid count as water."""
        if not (0 <= r < rows and 0 <= c < cols):
            return WATER in kinds
        return cp.any([grid[r, c] == k for k in kinds])

    def water(r, c):
        return one_of(r, c, [WATER])

    model = cp.Model()

    # The hints are cells whose content is known from the start.
    for r, c, v in hints:
        model += grid[r, c] == v

    # Row and column sums: every non-water cell is a piece of a ship.
    for i in range(rows):
        model += cp.sum(grid[i, :] > WATER) == rowsum[i]
    for j in range(cols):
        model += cp.sum(grid[:, j] > WATER) == colsum[j]

    for r in range(rows):
        for c in range(cols):
            # Ships do not touch diagonally: all four diagonal neighbours of a ship cell are water.
            diagonals = [water(r + dr, c + dc) for dr in (-1, 1) for dc in (-1, 1)]
            model += (grid[r, c] > WATER).implies(cp.all(diagonals))

            # A submarine is surrounded by water on all four sides.
            model += (grid[r, c] == CIRCLE).implies(
                cp.all([water(r - 1, c), water(r + 1, c), water(r, c - 1), water(r, c + 1)]))

            # The left end of a ship continues to the right (middle or right end); the other
            # three neighbours are water.
            model += (grid[r, c] == LEFT).implies(cp.all([
                one_of(r, c + 1, [MIDDLE, RIGHT]),
                water(r, c - 1), water(r - 1, c), water(r + 1, c)]))

            # The right end of a ship continues to the left (middle or left end).
            model += (grid[r, c] == RIGHT).implies(cp.all([
                one_of(r, c - 1, [MIDDLE, LEFT]),
                water(r, c + 1), water(r - 1, c), water(r + 1, c)]))

            # The top end of a ship continues downward (middle or bottom end).
            model += (grid[r, c] == TOP).implies(cp.all([
                one_of(r + 1, c, [MIDDLE, BOTTOM]),
                water(r - 1, c), water(r, c - 1), water(r, c + 1)]))

            # The bottom end of a ship continues upward (middle or top end).
            model += (grid[r, c] == BOTTOM).implies(cp.all([
                one_of(r - 1, c, [MIDDLE, TOP]),
                water(r + 1, c), water(r, c - 1), water(r, c + 1)]))

            # A middle piece lies inside a ship that is either horizontal or vertical.
            horizontal = cp.all([one_of(r, c - 1, [LEFT, MIDDLE]), one_of(r, c + 1, [RIGHT, MIDDLE]),
                                 water(r - 1, c), water(r + 1, c)])
            vertical = cp.all([one_of(r - 1, c, [TOP, MIDDLE]), one_of(r + 1, c, [BOTTOM, MIDDLE]),
                               water(r, c - 1), water(r, c + 1)])
            model += (grid[r, c] == MIDDLE).implies(horizontal | vertical)

    # Fleet composition. Submarines (size 1) are counted directly.
    model += cp.sum(grid == CIRCLE) == fleet_counts[1]

    # A ship of size n is an end piece, n-2 middle pieces and the opposite end piece in a line
    # (the connection rules above make every run of ship pieces one such ship). Count the
    # windows of each size that read left-middle...-right or top-middle...-bottom.
    for size, count in fleet_counts.items():
        if size < 2:
            continue
        ships = []
        for r in range(rows):
            for c in range(cols - size + 1):
                ships.append(cp.all([grid[r, c] == LEFT, grid[r, c + size - 1] == RIGHT]
                                    + [grid[r, c + k] == MIDDLE for k in range(1, size - 1)]))
        for r in range(rows - size + 1):
            for c in range(cols):
                ships.append(cp.all([grid[r, c] == TOP, grid[r + size - 1, c] == BOTTOM]
                                    + [grid[r + k, c] == MIDDLE for k in range(1, size - 1)]))
        model += cp.sum(ships) == count

    # No ship of a size outside the fleet: every left or top end starts one of the ships
    # counted above, so the number of ends must equal the number of ships longer than 1.
    model += cp.sum(grid == LEFT) + cp.sum(grid == TOP) == sum(
        count for size, count in fleet_counts.items() if size > 1)

    return model, {"grid": grid}
