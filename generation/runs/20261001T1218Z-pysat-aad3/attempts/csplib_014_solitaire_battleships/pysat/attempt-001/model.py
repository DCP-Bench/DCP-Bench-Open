# Solitaire battleships: fill a grid so that every cell is water, a submarine or a part of
# a longer ship (left, right, top, bottom or middle). Ships lie horizontally or vertically,
# no two ships touch, even diagonally, the row and column counts of ship cells are given,
# the fleet has the listed number of ships of each size, and some cells are given as hints.
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def build(instance):
    rows, cols = instance["rows"], instance["cols"]
    rowsum, colsum = instance["rowsum"], instance["colsum"]  # ship cells per row / per column
    fleet = {size: count for size, count in instance["fleet_counts"]}  # ship size -> number of ships
    hints = instance["hints"]                                 # [row, col, cell code], 0-based
    WATER, CIRCLE, LEFT, RIGHT = instance["WATER"], instance["CIRCLE"], instance["LEFT"], instance["RIGHT"]
    TOP, BOTTOM, MIDDLE = instance["TOP"], instance["BOTTOM"], instance["MIDDLE"]  # CIRCLE = submarine
    codes = [WATER, instance["_SHIP"], CIRCLE, LEFT, RIGHT, TOP, BOTTOM, MIDDLE]

    pool = IDPool()
    # grid[r][c] holds one of the cell codes. The direct encoding gives the literal
    # grid[r][c].equals(code) for "this cell has that code", which the rules below are written in.
    grid = [[Integer(f"grid_{r}_{c}", min(codes), max(codes), vpool=pool) for c in range(cols)]
            for r in range(rows)]
    engine = IntegerEngine(vars=[cell for row in grid for cell in row], vpool=pool)
    cnf = engine.clausify()

    def is_(r, c, *wanted):
        """Literals for "cell (r, c) has one of the wanted codes". Outside the grid there is only
        water: the result is the constant True for WATER and the constant False otherwise."""
        if not (0 <= r < rows and 0 <= c < cols):
            return [True] if WATER in wanted else []
        return [grid[r][c].equals(code) for code in wanted]

    def add_clause(*lits):
        """Add the disjunction of lits, each an int literal or a list of them, or the constants True and False."""
        clause = []
        for lit in lits:
            for item in (lit if isinstance(lit, list) else [lit]):
                if item is True:
                    return
                if item is not False:
                    clause.append(item)
        cnf.append(clause)

    def implies(antecedent, *requirements):
        """antecedent -> every requirement, each requirement being a list of alternative literals."""
        for requirement in requirements:
            add_clause(-antecedent, requirement)

    # the cells given as hints
    for r, c, code in hints:
        cnf.append(is_(r, c, code))

    # row and column counts: the number of non-water cells in each row and column
    non_water = [[-grid[r][c].equals(WATER) for c in range(cols)] for r in range(rows)]
    for r in range(rows):
        cnf.extend(CardEnc.equals(lits=non_water[r], bound=rowsum[r], vpool=pool,
                                  encoding=EncType.seqcounter).clauses)
    for c in range(cols):
        cnf.extend(CardEnc.equals(lits=[non_water[r][c] for r in range(rows)], bound=colsum[c],
                                  vpool=pool, encoding=EncType.seqcounter).clauses)

    for r in range(rows):
        for c in range(cols):
            ship = non_water[r][c]
            above, below = (r - 1, c), (r + 1, c)
            beside_l, beside_r = (r, c - 1), (r, c + 1)

            # ships do not touch diagonally: a ship cell has water on its four diagonal corners
            for dr in (-1, 1):
                for dc in (-1, 1):
                    implies(ship, is_(r + dr, c + dc, WATER))

            # a submarine is surrounded by water on its four sides
            for nr, nc in (above, below, beside_l, beside_r):
                implies(grid[r][c].equals(CIRCLE), is_(nr, nc, WATER))

            # the left end of a ship has the middle or the right end next to it on the right,
            # and water on its other three sides
            implies(grid[r][c].equals(LEFT), is_(*beside_r, MIDDLE, RIGHT), is_(*beside_l, WATER),
                    is_(*above, WATER), is_(*below, WATER))
            # the right end: middle or left end on the left, water on the other sides
            implies(grid[r][c].equals(RIGHT), is_(*beside_l, MIDDLE, LEFT), is_(*beside_r, WATER),
                    is_(*above, WATER), is_(*below, WATER))
            # the top end: middle or bottom end below, water on the other sides
            implies(grid[r][c].equals(TOP), is_(*below, MIDDLE, BOTTOM), is_(*above, WATER),
                    is_(*beside_l, WATER), is_(*beside_r, WATER))
            # the bottom end: middle or top end above, water on the other sides
            implies(grid[r][c].equals(BOTTOM), is_(*above, MIDDLE, TOP), is_(*below, WATER),
                    is_(*beside_l, WATER), is_(*beside_r, WATER))

            # a middle part sits inside a horizontal ship (left part or middle on its left, middle or
            # right part on its right, water above and below) or inside a vertical one
            horizontal, vertical = pool.id(("horizontal", r, c)), pool.id(("vertical", r, c))
            cnf.append([-grid[r][c].equals(MIDDLE), horizontal, vertical])
            implies(horizontal, is_(*beside_l, LEFT, MIDDLE), is_(*beside_r, RIGHT, MIDDLE),
                    is_(*above, WATER), is_(*below, WATER))
            implies(vertical, is_(*above, TOP, MIDDLE), is_(*below, BOTTOM, MIDDLE),
                    is_(*beside_l, WATER), is_(*beside_r, WATER))

    # the fleet: the listed number of submarines
    cnf.extend(CardEnc.equals(lits=[grid[r][c].equals(CIRCLE) for r in range(rows) for c in range(cols)],
                              bound=fleet[1], vpool=pool, encoding=EncType.seqcounter).clauses)

    # the fleet: a ship of size n is a left (top) end, n-2 middle parts and a right (bottom) end in
    # a line. ship_here is true exactly when such a ship starts at that cell, so the count is exact.
    for size, count in fleet.items():
        if size < 2:
            continue
        starts = []
        for r in range(rows):
            for c in range(cols):
                for dr, dc, first, last in ((0, 1, LEFT, RIGHT), (1, 0, TOP, BOTTOM)):
                    end_r, end_c = r + dr * (size - 1), c + dc * (size - 1)
                    if end_r >= rows or end_c >= cols:
                        continue
                    parts = [grid[r][c].equals(first), grid[end_r][end_c].equals(last)]
                    parts += [grid[r + dr * k][c + dc * k].equals(MIDDLE) for k in range(1, size - 1)]
                    ship_here = pool.id(("ship", size, r, c, dr))
                    for part in parts:
                        cnf.append([-ship_here, part])
                    cnf.append([ship_here] + [-part for part in parts])
                    starts.append(ship_here)
        cnf.extend(CardEnc.equals(lits=starts, bound=count, vpool=pool, encoding=EncType.seqcounter).clauses)

    # no ship of a size the fleet does not list: every left or top end starts one of the ships counted
    # above, so the number of left and top ends equals the number of ships longer than one cell
    ends = [grid[r][c].equals(code) for r in range(rows) for c in range(cols) for code in (LEFT, TOP)]
    cnf.extend(CardEnc.equals(lits=ends, bound=sum(count for size, count in fleet.items() if size > 1),
                              vpool=pool, encoding=EncType.seqcounter).clauses)

    return cnf, {"grid": grid}
