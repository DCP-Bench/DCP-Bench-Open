"""Solitaire battleships (CSPLib 014) in Paramita.

A 10x10 grid holds a fleet: battleships (length 4), cruisers (3), destroyers (2)
and submarines (1). Ships are straight and no two ships touch, not even
diagonally. Row and column sums count the occupied squares. Some squares are
given as hints. Each cell is water, a submarine, or a ship part (left, right,
top, bottom, middle).

Instance fields used: rows, cols, rowsum, colsum, fleet_counts, hints, and the
cell codes WATER, CIRCLE, LEFT, RIGHT, TOP, BOTTOM, MIDDLE. _SHIP is not used:
the output grid has no generic ship code.
"""

from paramita.modelling import Bool, And, Or, If, Iff


def build(instance):
    nr, nc = instance["rows"], instance["cols"]
    rowsum, colsum = instance["rowsum"], instance["colsum"]
    fleet = instance["fleet_counts"]  # [length, count] pairs
    hints = instance["hints"]         # [row, col, code]

    names = ["WATER", "CIRCLE", "LEFT", "RIGHT", "TOP", "BOTTOM", "MIDDLE"]
    code = {k: instance[k] for k in names}
    by_code = {v: k for k, v in code.items()}
    occupied = [k for k in names if k != "WATER"]

    # x[r][c][k]: cell (r, c) holds the code k (one-hot)
    x = [[{k: Bool(f"x_{r}_{c}_{k}") for k in names} for c in range(nc)] for r in range(nr)]

    def inside(r, c):
        return 0 <= r < nr and 0 <= c < nc

    cons = []

    # every cell holds exactly one code
    for r in range(nr):
        for c in range(nc):
            cons.append(sum(x[r][c][k] for k in names) == 1)

    def conjunction(r, c, water, sets):
        """Terms that must all hold around (r, c). water: offsets that must be water.
        sets: {offset: codes} where the neighbour must hold one of the codes.
        Returns None when a required neighbour is off the grid (alternative impossible)."""
        out = []
        for dr, dc in water:
            if inside(r + dr, c + dc):
                out.append(x[r + dr][c + dc]["WATER"])
        for (dr, dc), allowed in sets.items():
            if not inside(r + dr, c + dc):
                return None
            opts = [x[r + dr][c + dc][k] for k in allowed]
            out.append(opts[0] if len(opts) == 1 else Or(opts))
        return out

    def piece_rule(r, c, piece, alternatives):
        """If the cell holds `piece`, one of the alternatives (lists of terms) holds."""
        alts = [a for a in alternatives if a is not None]
        if any(a == [] for a in alts):
            return  # an alternative with no requirement always holds
        if not alts:
            cons.append(~x[r][c][piece])
            return
        conj = [a[0] if len(a) == 1 else And(a) for a in alts]
        cons.append(If(x[r][c][piece], conj[0] if len(conj) == 1 else Or(conj)))

    all8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    # ships do not touch, even diagonally: a piece's neighbours are water except the
    # ship parts that continue it in line
    for r in range(nr):
        for c in range(nc):
            # submarine: all eight neighbours are water
            piece_rule(r, c, "CIRCLE", [conjunction(r, c, all8, {})])

            # left end of a horizontal ship: continues to the right, water elsewhere
            piece_rule(r, c, "LEFT", [conjunction(r, c, [o for o in all8 if o != (0, 1)],
                                                  {(0, 1): ["RIGHT", "MIDDLE"]})])

            # right end of a horizontal ship: continues to the left, water elsewhere
            piece_rule(r, c, "RIGHT", [conjunction(r, c, [o for o in all8 if o != (0, -1)],
                                                   {(0, -1): ["LEFT", "MIDDLE"]})])

            # top end of a vertical ship: continues downwards, water elsewhere
            piece_rule(r, c, "TOP", [conjunction(r, c, [o for o in all8 if o != (1, 0)],
                                                 {(1, 0): ["BOTTOM", "MIDDLE"]})])

            # bottom end of a vertical ship: continues upwards, water elsewhere
            piece_rule(r, c, "BOTTOM", [conjunction(r, c, [o for o in all8 if o != (-1, 0)],
                                                    {(-1, 0): ["TOP", "MIDDLE"]})])

            # middle of a ship: horizontal (parts on both sides) or vertical (parts above and below)
            piece_rule(r, c, "MIDDLE", [
                conjunction(r, c, [(-1, -1), (-1, 0), (-1, 1), (1, -1), (1, 0), (1, 1)],
                            {(0, -1): ["LEFT", "MIDDLE"], (0, 1): ["RIGHT", "MIDDLE"]}),
                conjunction(r, c, [(-1, -1), (-1, 1), (1, -1), (1, 1), (0, -1), (0, 1)],
                            {(-1, 0): ["TOP", "MIDDLE"], (1, 0): ["BOTTOM", "MIDDLE"]}),
            ])

    # fleet: each ship of a given length is counted once, from its first cell.
    # A horizontal ship of length L starts at LEFT, has MIDDLE cells, and ends at RIGHT;
    # a vertical one starts at TOP and ends at BOTTOM.
    for length, count in fleet:
        starts = []
        if length == 1:
            starts = [x[r][c]["CIRCLE"] for r in range(nr) for c in range(nc)]
        else:
            for r in range(nr):
                for c in range(nc):
                    if inside(r, c + length - 1):
                        parts = [x[r][c]["LEFT"]] + [x[r][c + k]["MIDDLE"] for k in range(1, length - 1)] \
                            + [x[r][c + length - 1]["RIGHT"]]
                        h = Bool(f"hship_{length}_{r}_{c}")
                        cons.append(Iff(h, And(parts)))
                        starts.append(h)
                    if inside(r + length - 1, c):
                        parts = [x[r][c]["TOP"]] + [x[r + k][c]["MIDDLE"] for k in range(1, length - 1)] \
                            + [x[r + length - 1][c]["BOTTOM"]]
                        v = Bool(f"vship_{length}_{r}_{c}")
                        cons.append(Iff(v, And(parts)))
                        starts.append(v)
        cons.append(sum(starts) == count)

    # row and column sums: the number of occupied (non-water) squares
    for r in range(nr):
        cons.append(sum(x[r][c][k] for c in range(nc) for k in occupied) == rowsum[r])
    for c in range(nc):
        cons.append(sum(x[r][c][k] for r in range(nr) for k in occupied) == colsum[c])

    # hints: the given cells hold the given codes
    for r, c, value in hints:
        cons.append(sum([x[r][c][by_code[value]]]) == 1)

    # output: the code of each cell (WATER has code 0 and adds nothing)
    grid = [[sum(code[k] * x[r][c][k] for k in names if code[k] != 0) for c in range(nc)]
            for r in range(nr)]
    return cons, {"grid": grid}
